'''Simpson's paradox is simply that if two variables (y and z) have a weak
negative association with each other and a strong positive association with
a third variable (x), they will appear to have a positive association, which
only is revealed as false when they are categorized by the value of x.

This simple module offers visualization of Simpson's paradox for a toy dataset
where:
x is in [0, 1,..., xgroups)
y = x + y_noise
z = x + yz_assoc*y + z_noise

Simpson's paradox would occur whenever yz_assoc is negative.
This module allows visualization of Simpson's paradox for variable values of
yz_assoc, z_noise, and xgroups.
It can be called from the command line with optional args for yz_assoc, z_noise
and xgroups.
'''
import numpy as np
import matplotlib.pyplot as plt
import sys

def simpson(yz_assoc = -0.2, z_noise = 0.2, xgroups = 5, seed = 420):
    np.random.seed(seed)
    x = np.random.randint(xgroups, size = 200)
    y = np.empty(200, float)
    z = np.empty(200, float)

    for ii in range(xgroups):
        groupi = x==ii
        y[groupi] = ii + np.random.normal(size = groupi.sum())
        z[groupi] = ii + yz_assoc*y[groupi] \
                    + np.random.normal(scale = z_noise, size = groupi.sum())

    plt.scatter(y, z, c = x)
    plt.colorbar()
    plt.xlabel("y", size = 14)
    plt.ylabel("z", size = 14)
    plt.title("y and z appear to be positively correlated with each other\nbut they only share a positive correlation with x (color variable)")
    plt.show()
    
if __name__ == '__main__':
    yz_assoc, z_noise, xgroups = -0.2, 0.2, 5
    if len(sys.argv) == 2:
        yz_assoc = float(sys.argv[1])
    if len(sys.argv) == 3:
        z_noise = float(sys.argv[2])
    if len(sys.argv) == 4:
        xgroups = int(sys.argv[3])
    simpson(yz_assoc, z_noise, xgroups)