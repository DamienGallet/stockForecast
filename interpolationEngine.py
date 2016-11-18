from math import *
from ploting_utilities import *
import numpy as np

DEFAULT_KEY = -1
START_KEY = 0

# !! NB_EVAL_PTS > NB_COEFF !!
NB_COEFF = 3
NB_EVAL_PTS = 5

conditionsPowered = []
previousKey = START_KEY






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

def powerConditions(currentConditions, nbCoeff=NB_COEFF, key=DEFAULT_KEY):

    global previousKey
    global conditionsPowered

    if previousKey == key:
        return conditionsPowered

    powered = np.array([1]*len(currentConditions))
    poweredOne = np.array([currentConditions[x] for x in range(len(currentConditions))])
    powered = np.vstack( (powered.T, poweredOne) ).T

    for i in range(2,nbCoeff):
        raiseCoeff = lambda x: x[1]*x[-1]
        newColumn = [raiseCoeff(x) for x in powered]
        powered = np.vstack( (powered.T, newColumn) ).T
    return powered

def testExpectedOffset():
    t= np.array([[10,	20,	101],
    [11,	30,	105],
    [12,	40,	108]])
    d= powerConditions([2,3,4])
    print(sum(sum(np.dot(d,t))))


def getExpectedOffset(currentConditions, interpolationMatrix, key=DEFAULT_KEY):

    conditionsPowered = powerConditions(currentConditions,NB_COEFF,key)
    return sum(sum(np.multiply(conditionsPowered,interpolationMatrix)))


def getCoeff(x,y):

    n = len(x)
    coeffs = []
    C = powerConditions(x,len(x))
    invC = np.linalg.inv(C)
    coeffs = np.dot(invC,y)
    return coeffs


def getXs(rangeC, xToChange):

    xS = []
    delta = rangeC[1]-rangeC[0]
    offset = delta/(NB_EVAL_PTS - 1)
    current = rangeC[0]
    for i in range(NB_EVAL_PTS):
        currentMod = current
        if current-offset < xToChange and current+offset > xToChange:
            if xToChange > current:
                currentMod = (xToChange - current + offset) / 2 + (current - offset)
            else:
                currentMod = (current + offset) - (current + offset - xToChange) / 2

        xS.append(currentMod)
        current += offset

    return xS


def recomputeInterpolationMatrix(currentCondition, newValue, interpolationMatrix, ranges):

    for i in range(len(interpolationMatrix)):
        xValueToChange = currentCondition[i]
        currentCoeffs = interpolationMatrix[i]
        currentRange = ranges[i]
        currentXs = getXs(currentRange,xValueToChange)
        currentYs = []
        for x in currentXs:
            y = getExpectedOffset([x],[currentCoeffs])
            currentYs.append(y)

        currentXs.append(xValueToChange)
        currentYs.append(newValue)

        interpolationMatrix[i] = getCoeff(currentXs,currentYs)

    return interpolationMatrix


def correctInterpolationMatrix(currentCondition, offsetRecorded, interpolationMatrix, ranges):
    # Compute expected offset
    offsetExpected = getExpectedOffset(currentCondition,interpolationMatrix)

    # Make the difference with the recorded offset
    newValueCurrent = (offsetExpected + offsetRecorded) / 2

    return interpolationMatrix

#recomputeInterpolationMatrix([2],2,[[1,0,0]],[[0,3]])

# This algorithm comes from a nice article of http://blog.ivank.net/
# Spline computation
def evaluateSpline(x, xs, ys, ks):

    i=1
    while i<len(xs)-1 and xs[i]<x:
        i+=1

    t= (x-xs[i-1]) / (xs[i] - xs[i-1])

    a= ks[i-1]*(xs[i]-xs[i-1]) - (ys[i]-ys[i-1])
    b= -ks[i  ]*(xs[i]-xs[i-1]) + (ys[i]-ys[i-1])

    q = (1-t)*ys[i-1] + t*ys[i] + t*(1-t)*(a*(1-t)+b*t)

    return q

def swapRows(m, k, l):
    p = m[k]
    m[k] = m[l]
    m[l] = p


def solve(A):

    m = len(A)
    x = [0]*m
    for k in range(0, m, 1):
        # pivot for column
        i_max = 0
        vali = float("-inf")
        for i in range(k, m, 1):
            if A[i][k]>vali:
                i_max = i
                vali = A[i][k]
        swapRows(A, k, i_max)

        if A[i_max][k] == 0:
            print("matrix is singular!")

        # for all rows below pivot
        for i in range(k+1, m, 1):
            for j in range(k+1, m+1, 1):
                A[i][j] = A[i][j] - A[k][j] * (A[i][k] / A[k][k])
            A[i][k] = 0

    for i in range(m-1,0,-1):
        v = A[i][m] / A[i][i]
        x[i] = v
        for j in range(i-1,0,-1):
            A[j][m] -= A[j][i] * v
            A[j][i] = 0

    return x

def getDerivatives(xs, ys):

    n= len(xs)-1
    A = [[0]*(n+2) for i in range(n+1)]

    for i in range(1,n):

        A[i][i-1] = 1/(xs[i] - xs[i-1])
        A[i][i] = 2 * (1/(xs[i] - xs[i-1]) + 1/(xs[i+1] - xs[i]))

        A[i][i+1] = 1/(xs[i+1] - xs[i])

        A[i][n+1] = 3*( (ys[i]-ys[i-1])/ ((xs[i] - xs[i-1])*(xs[i] - xs[i-1]))
                         +(ys[i+1]-ys[i])/ ((xs[i+1] - xs[i])*(xs[i+1] - xs[i])))

    A[0][0  ] = 2/(xs[1] - xs[0])
    A[0][1  ] = 1/(xs[1] - xs[0])
    A[0][n+1] = 3 * (ys[1] - ys[0]) / ((xs[1]-xs[0])*(xs[1]-xs[0]))

    A[n][n-1] = 1/(xs[n] - xs[n-1])
    A[n][n  ] = 2/(xs[n] - xs[n-1])
    A[n][n+1] = 3 * (ys[n] - ys[n-1]) / ((xs[n]-xs[n-1])*(xs[n]-xs[n-1]))

    return solve(A)

def standardRange():
    tab = list(range(-200,201,40))
    return tab

def modifyStandardRange(xn):

    j = 0
    xs = standardRange()
    for i in range(len(xs)):
        if abs(xs[i]-xn) < 20:
            xs[i] = xn
            j= i

    return xs,j

def goodCondition(condition):

    if condition > 200:
        current = 200
    elif condition < -200:
        current = -200
    else:
        current = condition
    return current


def getNewIdentity(currentConditions, offsetRecorded, oldIdentity):

    for i in range(len(currentConditions)):
        itemConditionCurrent = goodCondition(currentConditions[i])

        (xs,j) = modifyStandardRange(itemConditionCurrent)
        ks = getDerivatives(xs,oldIdentity[i])
        valuesSpline = []
        for k in xs:
            currentOffset = evaluateSpline(itemConditionCurrent,xs,oldIdentity[i],ks)
            valuesSpline.append(currentOffset)


        newValue = (offsetRecorded + valuesSpline[j]) / 2
        valuesSpline[j] = newValue

        newValuesSpin = []
        ks = getDerivatives(xs,valuesSpline)
        for k in standardRange():
            currentOffset = evaluateSpline(k,xs,valuesSpline,ks)
            newValuesSpin.append(currentOffset)

        oldIdentity[i] = newValuesSpin

    return oldIdentity

def evaluateOffset(currentConditions, identity):

    sumOffset = 0

    for i in range(len(currentConditions)):
        condition = goodCondition(currentConditions[i])

        ks = getDerivatives(standardRange(), identity[i])
        sumOffset += evaluateSpline(condition,standardRange(),identity[i],ks)

    return sumOffset / len(currentConditions)

'''xs = [0,1,2]
ys = [1,2,1]
ks = getDerivatives(xs,ys)
for i in range(0,20,1):
    print(str(i/10.0)+' '+str(evaluateSpline(i/10.0,xs,ys,ks)))'''
