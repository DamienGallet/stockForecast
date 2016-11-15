import dataLoader as xdl
import interface as xit
import pandas as pd
from utilities import *
import ploting_utilities

def price_forecast(grades, company):
    forecast = pd.DataFrame(columns=['COMPANY','MONTH','FORECAST','GRADE','BEST_FORECAST','STRAIGHT_FORECAST'])

    minMonth = int(grades['MONTH'].min())
    maxMonth = int(grades['MONTH'].max())

    for monthEstimation in range(minMonth, maxMonth):
        xit.progressRatio(monthEstimation-minMonth, maxMonth-minMonth, "Forecast", 10)
        maskGradesMonth = (grades['COMPANY'] == company) & (grades['MONTH'] > monthEstimation - 5) & (grades['MONTH'] <= monthEstimation + 5)
        preds = grades.loc[maskGradesMonth]
        totalWeightMonth = 0
        totalWeightMonthB = 0
        weightedVals = []
        weightedValsB = []
        for j, pred in preds.iterrows():
            currentMonth = pred['MONTH']

            currentWeight = gauss_function(currentMonth, 1, monthEstimation, 2) * pred['GRADE']
            weightedVal = currentWeight * pred['FORECAST']

            currentWeightB = indicatrice_function(currentMonth,monthEstimation)
            weightedValB = currentWeightB * pred['FORECAST']

            totalWeightMonth += currentWeight
            totalWeightMonthB += currentWeightB

            weightedVals.append(weightedVal)
            weightedValsB.append(weightedValB)

        if totalWeightMonth > 0:
            estimation = sum(weightedVals) / totalWeightMonth
            estimationB = sum(weightedValsB) / totalWeightMonthB
        else :
            estimation = 0
            estimationB = 0

        # Best forecast
        bestForecast = estimation
        worstForecast = estimation
        maskGradesMonth = (grades['COMPANY'] == company) & (grades['MONTH'] == monthEstimation)
        thisMonth = preds.loc[maskGradesMonth]
        if len(thisMonth) > 0:
            index = thisMonth['GRADE'].argmax()
            bestForecast = preds.loc[index]['FORECAST'].item()
            index = thisMonth['GRADE'].argmin()
            worstForecast = preds.loc[index]['FORECAST'].item()

        forecast.loc[len(forecast)] = [company, monthEstimation, estimation, 0, bestForecast, estimationB]

    return forecast


def evaluateForecast(forecast, prices):
    for i, pred in forecast.iterrows():
        xit.progressRatio(i, len(forecast), "Forecast evaluation", 10)
        try:
            priceLine = prices.loc[int(pred['MONTH'])]
        except:
            continue
        if len(priceLine) == 1:
            price = priceLine['PRC']
            forecasted = pred['FORECAST']
            deviation = abs(price - forecasted) / price
            forecast.set_value(i, 'GRADE', deviation)
            forecast.set_value(i, 'OFFSET', price - forecasted)

    return forecast


def evaluateSinglePredictions(company, preds, prices):

    grades = pd.DataFrame(columns=['COMPANY', 'MONTH', 'PREDNO', 'ESTIMID', 'ALYSNAM', 'FORECAST', 'GRADE'],
                          index=range(len(preds)),
                          dtype=float)

    totalPred = len(preds)
    for i, row in preds.iterrows():
        val, date = grade(preds, prices, i)
        if val != -1:
            grades.loc[i] = [row['XCOMPANY'], date, 0, row['ESTIMID'], row['ALYSNAM'], row['VALUE'], val]
        else:
            preds.set_value(i, 'GRADE', val)
        xit.progressRatio(i, totalPred, "Pred analysis", 2)
    xit.progressRatio(totalPred, totalPred, "Pred analysis completed", 2)
    grades = grades.dropna()
    return grades


def getGrades(company, preds, prices, refresh=False, store=False):

    compute = False
    grades = None

    if not refresh:
        grades = xdl.getFromCache(company, xdl.DataType.PRED)
        if grades is None:
            compute = True
    else:
        compute = True

    if compute:
        grades = evaluateSinglePredictions(company, preds, prices)
    if store and compute:
        xdl.putToCache(company, xdl.DataType.PRED, grades)

    return grades


def absoluteForecast(company, preds, prices, refresh, store, allGrades):

    grades = getGrades(company, preds, prices, refresh, store)

    forecast = price_forecast(grades, company)
    forecast = evaluateForecast(forecast, prices)
    xdl.putToCache(company, xdl.DataType.FORECAST, forecast)

    allGrades = getMergedGrades(allGrades, grades)

    return forecast, grades, allGrades


def plotAbsolute(prices, preds, grades, forecast, company):
    datesF = list(forecast['MONTH'].values)
    for i in range(len(datesF)):
        datesF[i] = datesF[i]

    forecasts = list(forecast['FORECAST'].values)
    bestF = list(forecast['BEST_FORECAST'].values)
    straightF = list(forecast['STRAIGHT_FORECAST'].values)
    valprice = list(prices['PRC'].values)
    datesprice = list(prices.index.values)

    gradeDate = list(grades['MONTH'].values)
    gradePreds = list(grades['FORECAST'].values)
    gradeGrades = list(grades['GRADE'].values)

    ploting_utilities.plots2D([datesF, datesprice, datesF, datesF, gradeDate],
                              [forecasts, valprice, bestF, straightF, gradePreds],
                              [None,None,None,None,gradeGrades],
                              [False,False,False,False,True],
                              company)
