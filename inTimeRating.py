import numpy as np
import pandas as pd
from utilities import *
import math


DEFAULT_GRADE = 0
FORECAST_MEMORY = 50
ELDER_ADVANTAGE = 5


def initAnalystGradeData():

    grades = [0]*FORECAST_MEMORY
    dates = [0]*FORECAST_MEMORY

    return grades, dates

def getNewGrade(newGrades):

    sum = 0
    nbValues = 1
    for i in range(len(newGrades)):
        if newGrades[i] != 0:
            sum += newGrades[i]
        else:
            nbValues = i
            break

    return sum / (nbValues + 1)


def getAnalystGradeData(newData, newDate, oldGrades, oldDates, oldGrade):

    newGrades = [newData]
    newDates = [newDate]

    # THIS IS AWFUL
    newGrades += oldGrades[:-1]
    newDates += oldDates[:-1]

    newGrade = getNewGrade(newGrades)

    return newGrade, newGrades, newDates


def getAnalystGrade(analystGrades, estimid):
    try:
        return analystGrades.loc[estimid]['GRADE']
    except:
        return DEFAULT_GRADE


def getPredsForDate(preds, monthBeg, monthEnd, company):
    maskGradesMonth = (preds['OFTIC'] == company) \
                      & (preds['MONTH'] >= monthBeg-12) \
                      & (preds['MONTH'] <= monthEnd-12)
    try:
        return preds.loc[maskGradesMonth]
    except:
        return []


def computePrediction(pred, analystGrade, timeOffset):

    value = pred['VALUE']
    weight = analystGrade
    return value, weight


def updateGrades(analystGrades, preds, prices, month, company):

    currentPred = getPredsForDate(preds,month,month,company)
    for i, pred in currentPred.iterrows():
        # This part should be behind the try except
        (newData,newDate) = grade(currentPred, prices, i)

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
                                                                newDate,
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
