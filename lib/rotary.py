"""Position alignment for queries transferred between prompts."""
import torch
HEADS = 16

def rotate_half(x):
    a, b = (x[..., :x.shape[-1] // 2], x[..., x.shape[-1] // 2:])
    return torch.cat((-b, a), dim=-1)

def rerotate(model, x, delta):
    """Rotate post-RoPE vectors x [..., D] by a position offset delta using the model's rotary embedding."""
    if delta == 0:
        return x
    cos, sin = model.model.rotary_emb(x.float(), torch.tensor([[delta]], device=x.device))
    cos, sin = (cos[0, 0].float(), sin[0, 0].float())
    return (x.float() * cos + rotate_half(x.float()) * sin).to(x.dtype)

def rotation_check(model):
    g = torch.Generator(device='cuda').manual_seed(0)
    D = model.config.hidden_size // model.config.num_attention_heads
    x = torch.randn(1, HEADS, 1, D, device='cuda', generator=g)

    def rope(v, p):
        cos, sin = model.model.rotary_emb(v, torch.tensor([[p]], device='cuda'))
        return v * cos[0, 0] + rotate_half(v) * sin[0, 0]
    errs = []
    for p, d in ((10, 37), (300, -120), (700, 5), (5, 600)):
        a = rope(x, p + d)
        b = rerotate(model, rope(x, p), d).float()
        errs.append(float((a - b).abs().max() / a.abs().max()))
    assert max(errs) < 0.0001, errs
    return errs
