import numpy as np
import pandas as pd
import driver as drv
from utilities import *
import interface as xit
import ploting_utilities
from inTimeRating import *
from functionComparaison import *
import math

MONTH_BEG = 1150
MONTH_END = 1450


def getPredsOfDate(preds, monthBeg, monthEnd, company):
    maskGradesMonth = ((preds['MONTH'] >= monthBeg)
                      & (preds['MONTH'] <= monthEnd))
    try:
        return preds.loc[maskGradesMonth]
    except:
        return []

def getPriceOfDate(prices, monthBeg, monthEnd, company):
    maskGradesMonth = ((prices.index >= monthBeg)
                      & (prices.index <= monthEnd))
    try:
        val = prices.loc[maskGradesMonth]['PRC'].values[0]
        return val
    except:
        return 0

def forecastFunc(preds,prices,analystGrades,month,company):

    finalValue = 0
    finalWeight = 0
    for i, pred in preds.iterrows():
        analystGrade = getAnalystGrade(analystGrades,pred['ESTIMID'])
        timeOffset = abs(pred['MONTH'] - month)

        (value, weight) = computePrediction(pred,
                                            analystGrade,
                                            timeOffset)

        finalValue += value*weight
        finalWeight += weight

    if finalWeight == 0:
        return None

    return finalValue/finalWeight


def shortForecast(prices, predsP, company):

    forecast = pd.DataFrame(columns=['MONTH','VARIATION','FORECAST','STD'],
                            index=['MONTH'])

    analystGrades = pd.DataFrame(columns=['ESTIMID','ALYSNAM','GRADES','GRADE','DATES'])
    analystGrades.set_index('ESTIMID',inplace=True)
    analystGrades = analystGrades.fillna(value=0)
    analystGrades[['GRADES','DATES']].astype(object)


    # month is the month of the forecast
    for month in range(MONTH_BEG,MONTH_END):

        preds = getPredsOfDate(predsP, month-2, month-2, company)
        price = getPriceOfDate(prices, month-2,month-2, company)

        if price is None or price == 0 or len(preds) == 0:
            continue

        standardDeviation = preds['VALUE'].std()
        mean = preds['VALUE'].mean()

        variation = mean-price
        forecastV = forecastFunc(preds,prices,analystGrades,month,company)
        if forecastV is None:
            try:
                forecastV = forecast.loc[month-1]['FORECAST'].values
            except:
                forecastV = 0

        #print('Delta forecast mean : '+str(forecastV-mean)+' | Mean : '+str(mean))
        if standardDeviation is None:
            standardDeviation = 0

        try:
            previousForecast = forecast.loc[month-1]['FORECAST'].values
        except:
            previousForecast = 0
        if previousForecast is not None and previousForecast != 0:
            deltaForecast = forecastV - previousForecast
            forecastV = price + deltaForecast

        #forecast.loc[month] = [month,variation,forecastV,standardDeviation]
        forecast.set_value(month,'MONTH',month)
        forecast.set_value(month,'VARIATION',variation)
        forecast.set_value(month,'FORECAST',forecastV)
        forecast.set_value(month,'STD',standardDeviation)


        (analystGrades, preds) = updateGradesB(analystGrades, preds, price, month, company)

    analystGrades = forecast.fillna(0)
    return forecast


def updateGradesB(analystGrades, preds, price, month, company):

    for i, pred in preds.iterrows():
        # This part should be behind the try except
        newData = absoluteGradeFun(pred['VALUE'],price)

        analyst = pred['ESTIMID']
        exists = True
        try:
            analystData = analystGrades.loc[analyst]
            oldGrades = analystData['GRADES']
            oldDates = analystData['DATES']
            oldGrade = analystData['GRADE']
            alysnam = analystData['ALYSNAM']
        except:
            oldGrades, oldDates = initAnalystGradeData()
            oldGrade = DEFAULT_GRADE
            alysnam = pred['ALYSNAM']
            exists = False
            if pd.isnull(pred['ALYSNAM']):
                alysnam = 'UNKNOWN'



        if newData == -1:
            continue

        (newGrade, newGrades, newDates) = getAnalystGradeData(  newData,
                                                                month,
                                                                oldGrades,
                                                                oldDates,
                                                                oldGrade)
        if not exists:
            analystGrades.loc[analyst] = [alysnam,
                                          newGrades,
                                          newGrade,
                                          newDates]
        else:
            analystGrades.set_value(analyst, 'GRADES', newGrades)
            analystGrades.set_value(analyst, 'DATES', newDates)

        preds.set_value(i, 'GRADE', newGrade)

    return analystGrades, preds



def plotShortTerm(prices, forecast,company):

    datesF = list(forecast.index.values)[1:]
    datesP = list(prices.index.values)

    valuesF = list(forecast['FORECAST'].values)[1:]
    valuesP = list(prices['PRC'].values)

    variationP = list(forecast['FORECAST'].values)
    variationP = np.nan_to_num(variationP)
    variation = [-val for val in variationP]
    print(variation)
    minC = min(variation)
    maxC = max(variation)

    print(variation)
    print(forecast)

    ploting_utilities.plots2D([datesP,datesF],
                              [valuesP,valuesF],
                              [None,variation],
                              [False,True],
                              company,
                              minC,
                              maxC)


def computeAndPlotShort(prices, preds, company):
    forecast = shortForecast(prices, preds, company)
    score = evaluateForecast(forecast,prices)
    plotShortTerm(prices,forecast,company+' '+str(score))

