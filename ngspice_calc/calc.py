import numpy as np

def cross_over_points(t, v, target):
    crossings = []
    for i in range(1, len(v)):
        if v[i-1] < target <= v[i]:
            frac = (target - v[i])