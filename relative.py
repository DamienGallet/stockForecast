import numpy as np
import pandas as pd
import driver as drv
from utilities import *

DEFAULT_GRADE = 0
FORECAST_MEMORY = 50
ELDER_ADVANTAGE = 5


def initAnalystGradeData():

    grades = [0]*FORECAST_MEMORY
    dates = [0]*FORECAST_MEMORY

    return grades, dates

def getAnalystGradeData(newData, newDate, oldGrades, oldDates):

    newGrades = [newData]
    newDates = [newDate]

    # THIS IS AWFUL
    newGrades += oldGrades[:-2]
    newDates += oldDates[:-2]

    # FORECAST_MEMORY-1 to preserve an advantage for old analysts
    newGrade = sum(newGrades)/(FORECAST_MEMORY-ELDER_ADVANTAGE)

    return newGrade, newGrades, newDates


def getAnalystGrade(analystGrades, estimid):
    try:
        return analystGrades.loc[estimid]
    except:
        return DEFAULT_GRADE


def getPredsForDate(preds, monthBeg, monthEnd, company):
    maskGradesMonth = (preds['OFTIC'] == company) \
                      & (preds['MONTH'] >= monthBeg) \
                      & (preds['MONTH'] <= monthEnd)
    try:
        return preds.loc[maskGradesMonth]
    except:
        return []


def evaluationEngine(preds, prices,companies):
    """

    :type preds: pd.DataFrame
    :type prices: pd.DataFrame
    :type companies: list
    :rtype: DataFrame
    """
    preds.sort(['MONTH'],inplace=True)
    forecastFAll = {}

    analystGrades = pd.DataFrame(columns=['ESTIMID','ALYSNAM','GRADES','GRADE','DATES'])
    analystGrades.set_index('ESTIMID',inplace=True)

    for company in companies:
        forecastC = pd.DataFrame(columns=['COMPANY','FORECAST','GRADE'],
                                index=range(1150,1450))
        forecastC.index.name = 'MONTH'
        forecastFAll[company] = forecastC

    for month in range(1200,1400):
        step(preds, prices, analystGrades, forecast, month)

    return


def computePrediction(pred, analystGrade, timeOffset):

    value = pred['FORECAST']
    weight = analystGrade
    return value, weight


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


def updateGrades(analystGrades, preds, prices, month, company):

    currentPred = getPredsForDate(preds,month,month,company)
    for i, pred in currentPred.iterrows():
        analyst = pred['ESTIMID']
        try:
            analystData = analystGrades.loc[analyst]
            oldGrades = analystData['GRADES']
            oldDates = analystData['DATES']
            alysnam = analystData['ALYSNAM']
        except:
            oldGrades, oldDates = initAnalystGradeData()
            alysnam = pred['ALYSNAM']

        newDate = pred['MONTH']
        newData = grade(currentPred, prices, i)

        (newGrade, newGrades, newDates) = getAnalystGradeData(  newData,
                                                                newDate,
                                                                oldGrades,
                                                                oldDates)

        analystGrades.loc[analyst] = [alysnam,
                                      newGrades,
                                      newGrade,
                                      newDates]

    return analystGrades


def step(preds, prices, analystGrades, forecastFAll, month):

    for company,forecastF in forecastFAll.items:
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
        analystGrades = updateGrades(analystGrades, preds, prices, month, company)
    return

