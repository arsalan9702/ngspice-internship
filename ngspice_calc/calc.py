import numpy as np


def avg_rms(t, x, t_start, t_end, eps=None):
    """
    Compute average and RMS of x over [t_start, t_end].
    Trapezoidal integration     with eps tolerance for boundary handling.
    """
    if eps is None:
        eps = 1e-3 * (t_end - t_start)

    sum_avg = 0.0
    sum_rms = 0.0

    t_last = t[0]
    y_last = x[0]
    n = len(t)

    for i in range(n):
        t0 = t[i]
        y0 = x[i]

        if (t_end - t_last) > (-eps):
            if (t_last - t_start) > (-eps):
                if (t_end - t0) > (-eps):
                    delta_t = t0 - t_last
                    sum_avg += 0.5 * delta_t * (y_last + y0)
                    sum_rms += 0.5 * delta_t * (y_last*y_last + y0*y0)
                else:
                    y1 = y_last + ((y0-y_last)/(t0-t_last)) * (t_end-t_last)
                    delta_t = t_end - t_last
                    sum_avg += 0.5 * delta_t * (y_last + y1)
                    sum_rms += 0.5 * delta_t * (y_last*y_last + y1*y1)
            else:
                if (t0 - t_start) > (-eps):
                    y1 = y_last + ((y0-y_last)/(t0-t_last)) * (t_start-t_last)
                    delta_t = t0 - t_start
                    sum_avg += 0.5 * delta_t * (y1 + y0)
                    sum_rms += 0.5 * delta_t * (y1*y1 + y0*y0)
        t_last = t0
        y_last = y0

    x_avg = sum_avg / (t_end - t_start)
    x_rms = np.sqrt(sum_rms / (t_end - t_start))
    return [x_avg, x_rms]


def min_max(t, x, t_start, t_end):
    """
    Find min and max of x between t_start and t_end.
    """
    x_min =  1.0e20
    x_max = -1.0e20
    n = len(t)

    for i in range(1, n):
        t1 = t[i]
        x1 = x[i]
        if (t1 >= t_start) and (t1 <= t_end):
            if x1 < x_min: x_min = x1
            if x1 > x_max: x_max = x1

    return [x_min, x_max]


def cross_over_points(t, x, t_start, t_end, x0):
    """
    Find times where x crosses x0.
    Returns (l_positive, l_negative):
        l_positive: crossings with positive slope
        l_negative: crossings with negative slope
    """
    l_positive = []
    l_negative = []

    n = len(t)
    t_old = t[0]
    x_old = x[0]

    for i in range(1, n):
        t_new = t[i]
        x_new = x[i]

        if (x_new == x0) and (x_old == x0):
            continue
        if x_new >= x0:
            if x_old <= x0:
                if (t_old >= t_start) and (t_new <= t_end):
                    t_cross = t_old + (x0-x_old)*(t_new-t_old)/(x_new-x_old)
                    l_positive.append(t_cross)
        if x_new <= x0:
            if x_old >= x0:
                if (t_old >= t_start) and (t_new <= t_end):
                    t_cross = t_old + (x0-x_old)*(t_new-t_old)/(x_new-x_old)
                    l_negative.append(t_cross)
        t_old = t_new
        x_old = x_new

    return l_positive, l_negative