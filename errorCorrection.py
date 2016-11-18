import numpy as np
import pandas as pd
import driver as drv
from utilities import *
import interface as xit
import ploting_utilities
import math
from inTimeRating import *
from interpolationEngine import *
from functionComparaison import *

MONTH_BEG = 1212
MONTH_END = 1360

def getFreshIdentity():
    return [[0]*11 for i in range(11)]

def errorCorrectionForecast(preds, prices,companies):
    """

    :type preds: pd.DataFrame
    :type prices: pd.DataFrame
    :type companies: list
    :rtype analystGrades: DataFrame
    :rtype forecastFAll: {}
    """
    preds.sort_values(by=['MONTH'],inplace=True)
    forecastFAll = {}

    analystGrades = pd.DataFrame(columns=['ESTIMID','ALYSNAM','GRADES','GRADE','DATES','IDENTITY'])
    analystGrades.set_index('ESTIMID',inplace=True)
    analystGrades= analystGrades.fillna(value=0)
    analystGrades[['GRADES','DATES']].astype(object)

    for company in companies:
        forecastC = pd.DataFrame(columns=['COMPANY', 'FORECAST', 'OFFSET'],
                                index=range(MONTH_BEG, MONTH_END))
        forecastC.index.name = 'MONTH'
        forecastFAll[company] = forecastC

    for month in range(MONTH_BEG,MONTH_END):
        xit.progressRatio(month, MONTH_END - MONTH_BEG, "Offset Corrector forecast", 10)
        (analystGrades, preds, forecastFAll) = step(preds, prices, analystGrades, forecastFAll, month)

    return analystGrades, preds, forecastFAll


def forecast(preds,prices,analystGrades,month,company,marketState):

    finalValue = 0
    finalWeight = 0
    sumOffset = 0
    for i, pred in preds.iterrows():
        if pred['HORIZON'] != 12:
            continue
        analystGrade = getAnalystGrade(analystGrades,pred['ESTIMID'])

        try:
            identity = analystGrades.loc[pred['ESTIMID']]['IDENTITY']
        except:
            continue
        offset = evaluateOffset(marketState,identity)

        value = pred['VALUE']*offset + pred['VALUE']
        print('Init value : '+str(pred['VALUE'])+' | Offset :'+str(offset)+' | Forecast :'+str(value))

        weight = pow(analystGrade,1.5)

        finalValue += value*weight
        sumOffset += offset * 100
        finalWeight += weight

    if finalWeight == 0:
        return None, None

    return finalValue/finalWeight, sumOffset/finalWeight


def interestingMonths():

    return [-24,-18,-14,-11,-9,-7,-5,-4,-3,-2,-1]


def evaluateMarketConditions(prices, month):

    currentPrice = getPrice(prices, month)
    if currentPrice == 0:
        return []

    months = interestingMonths()
    marketConditions = []
    for monthO in months:
        price = getPrice(prices,month+monthO)
        marketConditions.append((price/currentPrice)*100-100)

    return marketConditions



def step(preds, prices, analystGrades, forecastFAll, month):

    marketEval = evaluateMarketConditions(prices, month)

    for company,forecastF in forecastFAll.items():
        # It's ok to get the preds of current month
        currentPreds = getPredsForDate(preds, month+12, month+12, company)
        if len(preds) == 0:
            continue

        # Get preds for this month and this company
        (forecastC,offset) = forecast(currentPreds, prices, analystGrades, month, company, marketEval)
        if forecastC is not None:
            forecastF.loc[month+12] = [company, forecastC, 0]
        else:
            try:
                forecastF.loc[month+12] = forecastF.loc[month-1+12]
            except:
                forecastF.loc[month+12] = [company, forecastC, 0]

        # Grade the analysts
        (analystGrades, currentPreds) = updateGradesAndIdentity(analystGrades, currentPreds, prices, month, company, marketEval)

    return analystGrades, preds, forecastFAll


def plotErrorCorrection(prices, forecast, preds, company):

    datesF = list(forecast.index.values)[1:]
    datesP = list(prices.index.values)

    valuesF = list(forecast['FORECAST'].values)[1:]
    valuesP = list(prices['PRC'].values)
    colorF = list(forecast['OFFSET'].values)[1:]

    datesPred = list(preds['MONTH'].values)
    valuesPred = list(preds['VALUE'].values)
    variationP = list([0]*len(valuesPred))
    for i in range(len(datesPred)):
        datesPred[i] = datesPred[i]+12

    minC = min(variationP)
    maxC = max(variationP)
    '''variationP = list(forecast['VALUES'].values)
    variationP = np.nan_to_num(variationP)
    variation = [-val for val in variationP]
    print(variation)
    minC = min(variation)
    maxC = max(variation)

    print(variation)
    print(forecast)'''

    ploting_utilities.plots2D([datesP,datesF,datesPred],
                              [valuesP,valuesF,valuesPred],
                              [None,None,variationP],
                              [False,False,True],
                              company,
                              minC,
                              maxC)


def updateGradesAndIdentity(analystGrades, currentPred, prices, month, company,marketState):

    for i, pred in currentPred.iterrows():
        analyst = pred['ESTIMID']
        exists = True
        try:
            analystData = analystGrades.loc[analyst]
            oldGrades = analystData['GRADES']
            oldDates = analystData['DATES']
            oldGrade = analystData['GRADE']
            alysnam = analystData['ALYSNAM']
            identity = analystData['IDENTITY']
        except:
            oldGrades, oldDates = initAnalystGradeData()
            oldGrade = DEFAULT_GRADE
            identity = getFreshIdentity()
            alysnam = pred['ALYSNAM']
            exists = False
            if pd.isnull(pred['ALYSNAM']):
                alysnam = 'UNKNOWN'

        # This part should be behind the try except
        realPrice = getPrice(prices,month+pred['HORIZON'])
        offset = evaluateOffset(marketState,identity)
        value = pred['VALUE']*offset + pred['VALUE']
        offsetRecorded = realPrice/value
        (newData,newDate) = grade(currentPred, prices, i)


        if newData == -1:
            continue

        (newGrade, newGrades, newDates) = getAnalystGradeData(  newData,
                                                                newDate,
                                                                oldGrades,
                                                                oldDates,
                                                                oldGrade)
        if not exists:
            analystGrades.loc[analyst] = [alysnam,
                                          newGrades,
                                          newGrade,
                                          newDates,
                                          identity]
        else:
            analystGrades.set_value(analyst, 'GRADES', newGrades)
            analystGrades.set_value(analyst, 'DATES', newDates)
            analystGrades.set_value(analyst, 'IDENTITY', getNewIdentity(marketState,offsetRecorded,identity))


        currentPred.set_value(i, 'GRADE', newGrade)

    return analystGrades, currentPred


def computeAndPlotError(prices, preds, company):
    (analystGrades, preds, forecastFAll) = errorCorrectionForecast(preds,prices,[company])
    forecastFAll[company] = forecastFAll[company].fillna(0)
    print(analystGrades)
    print(forecastFAll[company])
    score = evaluateForecast(forecastFAll[company],prices)
    plotErrorCorrection(prices,forecastFAll[company],preds,company+' '+str(score))
