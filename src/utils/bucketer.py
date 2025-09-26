def bucket_from_p(p: float) -> str:
    """
    Map percentage p (0-100) to risk bucket.
    Safe:    p < 50
    Buffer:  50 <= p < 70
    Warning: 70 <= p < 85
    High-Risk: p >= 85
    """
    if p < 50:
        return "Safe"
    if p < 70:
        return "Buffer"
    if p < 85:
        return "Warning"
    return "High-Risk"
