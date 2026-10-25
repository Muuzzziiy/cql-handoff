"""Native per-loop Ouro readouts, reusable across pinned model sizes.

No attention intervention. The author backbone already returns the normalized
state used by its early-exit head at each loop; never apply another final norm.
"""
from pathlib import Path
import importlib.util
import sys
import types
import time
import torch
from torch.nn.attention import sdpa_kernel, SDPBackend

def author_module(directory):
    directory = Path(directory)
    package = '_research_native_ouro_readout'
    key = package + '.modeling_ouro'
    if key in sys.modules:
        assert Path(sys.modules[key].__file__).parent == directory
        return sys.modules[key]
    pkg = types.ModuleType(package)
    pkg.__path__ = [str(directory)]
    sys.modules[package] = pkg
    for stem in ('configuration_ouro', 'modeling_ouro'):
        name = package + '.' + stem
        spec = importlib.util.spec_from_file_location(name, directory / (stem + '.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return module

def load_model(directory, expected_layers):
    started = time.perf_counter()
    module = author_module(directory)
    config = module.OuroConfig.from_pretrained(str(directory), local_files_only=True)
    assert config.num_hidden_layers == expected_layers and config.total_ut_steps == 4
    config.use_cache = False
    config.early_exit_threshold = 1.0
    model, info = module.OuroForCausalLM.from_pretrained(str(directory), config=config, local_files_only=True, use_safetensors=True, dtype=torch.bfloat16, attn_implementation='sdpa', output_loading_info=True, low_cpu_mem_usage=True)
    assert not any((info.get(k) for k in ('missing_keys', 'unexpected_keys', 'mismatched_keys', 'error_msgs'))), info
    model.eval().requires_grad_(False).to('cuda')
    assert all((p.dtype == torch.bfloat16 for p in model.parameters()))
    return (model, dict(seconds=time.perf_counter() - started, loading_info=info, physical_layers=expected_layers, loops=4, dtype='bfloat16', cache=False))

class NativeCounter:

    def __init__(self, model):
        self.calls = []
        self.handles = []
        for i, layer in enumerate(model.model.layers):

            def observe(_m, _a, kw, i=i):
                self.calls.append((int(kw['current_ut']), i))
            self.handles.append(layer.self_attn.register_forward_pre_hook(observe, with_kwargs=True))

    def close(self):
        for h in self.handles:
            h.remove()

@torch.inference_mode()
def read_all_loops(model, ids, seed):
    """One native four-loop backbone, four ordinary last-token exit heads."""
    assert ids.shape[0] == 1 and model.model.total_ut_steps == model.config.total_ut_steps == 4
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    counter = NativeCounter(model)
    try:
        with sdpa_kernel(SDPBackend.FLASH_ATTENTION):
            output, states, gates = model.model(input_ids=ids, attention_mask={'full_attention': None}, use_cache=False, past_key_values=None)
            assert len(states) == len(gates) == 4 and output.past_key_values is None
            vectors = [model.lm_head(h[:, -1:, :])[0, 0].float().cpu().numpy().copy() for h in states]
        assert counter.calls == [(r, l) for r in range(4) for l in range(len(model.model.layers))]
        import numpy as np
        result = np.stack(vectors)
        assert np.isfinite(result).all()
        return (result, dict(actual_loops=4, layer_calls=len(counter.calls), exit_heads=4))
    finally:
        counter.close()

@torch.inference_mode()
def author_stopped_forward(model, ids, depth, seed):
    """Independent official CausalLM endpoint for the small engineering queue."""
    original = (model.model.total_ut_steps, model.config.total_ut_steps)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    counter = NativeCounter(model)
    try:
        model.model.total_ut_steps = model.config.total_ut_steps = depth
        with sdpa_kernel(SDPBackend.FLASH_ATTENTION):
            output = model(input_ids=ids, attention_mask={'full_attention': None}, use_cache=False, past_key_values=None, use_weighted_exit=False, exit_at_step=depth - 1, exit_threshold=1.0, logits_to_keep=1)
        assert counter.calls == [(r, l) for r in range(depth) for l in range(len(model.model.layers))]
        return output.logits[0, -1].float().cpu().numpy().copy()
    finally:
        model.model.total_ut_steps, model.config.total_ut_steps = original
        counter.close()
