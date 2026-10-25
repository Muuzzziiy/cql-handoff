def span_mask(text, offsets, start, end):
    mask = [b > start and a < end for a, b in offsets]
    assert any(mask)
    for selected, (a, b) in zip(mask, offsets):
        if selected:
            assert not text[a:min(b, start)].strip() if a < start else True
            assert not text[max(a, end):b].strip() if b > end else True
    return mask
