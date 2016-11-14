from math import *
from ploting_utilities import *

def FFT(samples):

    n = len(samples)

    if n==1:
        return samples

    fourierTransform = [10] * n

    a = [s for s in range(0,n,2)]
    b = [s for s in range(1,n,2)]

    A = FFT(a)
    B = FFT(b)

    omegaN = exp(-2*pi/n)
    omega = 1

    for k in range(0,int(n/2)):
        fourierTransform[k] = A[k] + omega*B[k]
        fourierTransform[int(n/2)+k] = A[k] - omega*B[k]
        omega *= omegaN

    return fourierTransform

def tests():
    sample = []
    for i in range(0,100):
        sample.append(cos(i))

    plot2D(range(0,100),sample)

    fft = FFT(sample)
    plot2D(range(0,100),fft)
    print(len(fft))

    pause()


tests()

