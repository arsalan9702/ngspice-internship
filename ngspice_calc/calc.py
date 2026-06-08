import numpy as np

def cross_over_points(t, v, target):
    crossings = []
    for i in range(1, len(v)):
        if v[i-1] < target <= v[i]:
            frac = (target - v[i]) / (v[i] - v[i-1])
            crossings.append(t[i-1] + frac * (t[i] - t[i-1]))
    return crossings

def avg_rms(t, v, t_start=None, t_end=None):
    if t_start is None: t_start = t[0]
    if t_end   is None: t_end   = t[-1]
    mask = (t >= t_start) & (t <= t_end)
    t_ = t[mask]
    v_ = v[mask]
    avg = np.trapezoid(v_,  t_) / (t_[-1] - t_[0])
    rms = np.sqrt(np.trapezoid(v_**2, t_) / (t_[-1] - t_[0]))
    return avg, rms