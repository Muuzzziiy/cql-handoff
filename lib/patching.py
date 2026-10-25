"""Generic attention operand replacement at caller-supplied coordinates."""
import torch
import torch.nn.functional as F
from . import ouro_advisor_stagecd as A
HEADS = 16

class Sel:
    """Replace operands at (layers, heads, mask) with source values at the given loops; capture at capture_loop."""

    def __init__(self, model, masks, spec, loops, source=None, capture_loop=None):
        self.model, self.masks, self.spec, self.loops, self.source, self.capture_loop = (model, masks, spec, set(loops), source, capture_loop)
        self.own = {}
        self.captured = {}
        self.orig = F.scaled_dot_product_attention
        self.handles = []
        self.calls = 0

    def __enter__(self):
        for i, layer in enumerate(self.model.model.layers):

            def before(_m, _a, kw, i=i):
                self.active = (int(kw['current_ut']) + 1, i)
            self.handles.append(layer.register_forward_pre_hook(before, with_kwargs=True))
        F.scaled_dot_product_attention = self.call
        return self

    def __exit__(self, *a):
        F.scaled_dot_product_attention = self.orig
        for h in self.handles:
            h.remove()

    def call(self, q, k, v, *args, **kw):
        loop, layer = self.active
        self.calls += 1
        ops = {'Q': q, 'K': k, 'V': v}
        if loop == 1 and self.source is None:
            self.own[layer] = {n: x.detach().clone() for n, x in ops.items()}
        if loop == self.capture_loop:
            self.captured[layer] = {n: x.detach().clone() for n, x in ops.items()}
        if loop in self.loops:
            src = self.own if self.source is None else self.source
            for name, region, layers, heads in self.spec:
                if layer not in layers:
                    continue
                hm = torch.zeros(HEADS, dtype=torch.bool, device=q.device)
                hm[list(heads)] = True
                w = hm[None, :, None, None] & self.masks[region][None, None, :, None]
                ops[name] = torch.where(w, src[layer][name], ops[name])
        return self.orig(ops['Q'], ops['K'], ops['V'], **kw)

def masks(c):
    m = A.masks_of(c)
    n = len(c['ids'])
    mem = [True] * n
    mem[-1] = False
    m['mem'] = torch.tensor(mem, dtype=torch.bool, device='cuda')
    return m

@torch.inference_mode()
def stopped(model, c, depth, seed, spec=(), loops=(), source=None, capture_loop=None):
    from .ouro_readout import author_stopped_forward
    with Sel(model, masks(c), spec, loops, source, capture_loop) as p:
        v = author_stopped_forward(model, torch.tensor([c['ids']], device='cuda'), depth, seed)
    return (v, p.captured)

@torch.inference_mode()
def all_loops(model, c, spec, seed):
    from .ouro_readout import read_all_loops
    with Sel(model, masks(c), spec, (2, 3, 4)):
        v, _ = read_all_loops(model, torch.tensor([c['ids']], device='cuda'), seed)
    return v
