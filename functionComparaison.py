import numpy as np
import pandas as pd
from utilities import *
import interface as xit
import ploting_utilities
import math


def evaluateForecast(forecast, prices):
    sum = 0
    pointNb = 0
    for i, pred in forecast.iterrows():
        try:
            xit.progressRatio(i, len(forecast), "Forecast evaluation", 10)
        except:
            pass

        try:
            priceLine = prices.loc[int(pred['MONTH'])]
            price = priceLine['PRC']
        except:
            continue

        forecasted = pred['FORECAST']
        if forecasted == 0:
            continue

        deviation = abs(price - forecasted) / price
        sum += deviation
        pointNb += 1

    if pointNb != 0:
        sum /= pointNb
    else:
        return 0

    return sum
