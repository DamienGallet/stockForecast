import numpy as np
import pandas as pd
import driver as drv
from utilities import *
import interface as xit
import ploting_utilities
import math
from inTimeRating import *

MONTH_BEG = 1150
MONTH_END = 1450


def relativeForecast(preds, prices,companies):
    """

    :type preds: pd.DataFrame
    :type prices: pd.DataFrame
    :type companies: list
    :rtype analystGrades: DataFrame
    :rtype forecastFAll: {}
    """
    preds.sort_values(by=['MONTH'],inplace=True)
    forecastFAll = {}

    analystGrades = pd.DataFrame(columns=['ESTIMID','ALYSNAM','GRADES','GRADE','DATES'])
    analystGrades.set_index('ESTIMID',inplace=True)
    analystGrades.fillna(value=0)
    analystGrades[['GRADES','DATES']].astype(object)

    for company in companies:
        forecastC = pd.DataFrame(columns=['COMPANY', 'FORECAST', 'GRADE'],
                                index=range(MONTH_BEG, MONTH_END))
        forecastC.index.name = 'MONTH'
        forecastFAll[company] = forecastC

    for month in range(MONTH_BEG,MONTH_END):
        xit.progressRatio(month, MONTH_END - MONTH_BEG, "Absolute forecast", 10)
        (analystGrades, preds, forecastFAll) = step(preds, prices, analystGrades, forecastFAll, month)

    return analystGrades, preds, forecastFAll


def forecast(preds,prices,analystGrades,month,company):

    preds = getPredsForDate(preds, month-2, month+2, company)
    if len(preds) == 0:
        return None

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


def step(preds, prices, analystGrades, forecastFAll, month):

    for company,forecastF in forecastFAll.items():
        # Get preds for this month and this company
        forecastC = forecast(preds, prices, analystGrades, month, company)
        if forecastC is not None:
            forecastF.loc[month] = [company, forecastC, 0]
        else:
            try:
                forecastF.loc[month] = forecastF.loc[month-1]
            except:
                forecastF.loc[month] = [company, forecastC, 0]

        # Grade the analysts
        (analystGrades, preds) = updateGrades(analystGrades, preds, prices, month, company)

    return analystGrades, preds, forecastFAll


def plotRelative(prices, preds, grades, forecast, company):
    datesF = list(forecast.index.values)
    for i in range(len(datesF)):
        datesF[i] = datesF[i]

    forecasts = list(forecast['FORECAST'].values)
    valprice = list(prices['PRC'].values)
    datesprice = list(prices.index.values)

    gradeDate = list(grades['MONTH'].values)
    gradePreds = list(grades['VALUE'].values)
    gradeGrades = list(grades['GRADE'].values)

    ploting_utilities.plots2D([datesF, datesprice, gradeDate],
                              [forecasts, valprice, gradePreds],
                              [None,None,gradeGrades],
                              [False,False,True],
                              company)

