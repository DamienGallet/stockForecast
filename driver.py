import dataLoader as xdl
import interface as xit
from datetime import timedelta
from datetime import datetime
import pandas as pd


companies = ["IBM"]

def grade(preds, prices, grades, i):

    currentPred = preds.loc[i]

    value, date = getRealPrice(currentPred,prices)
    if value == -1:
        return -1, 0

    pred = currentPred['VALUE']
    grade = absoluteGradeFun(pred, value)
    return grade, date

def getRealPrice(pred,prices):

    horizon = pred['HORIZON']
    crtMnth = pred['MONTH']
    price = -1
    line = prices.loc[crtMnth+horizon:crtMnth+horizon+3]
    if(len(line) == 0):
        return -1, 0
    goodLine = line.head(1)
    return goodLine['PRC'].item(), goodLine.index.item()


def absoluteGradeFun(forecastValue, finalPrice):
    if forecastValue == finalPrice:
        return 1

    if forecastValue < finalPrice:
        return forecastValue/finalPrice
    return finalPrice/forecastValue


def getPriceFromHorizon(init_date, horizon, prices) :
    start_date = init_date + timedelta(days=horizon*30-31)
    end_date = init_date + timedelta(days=horizon*30)
    mask = (prices['DATE'] > start_date) & (prices['DATE'] <= end_date)
    return prices.loc[mask]


if __name__ == "__main__":
    for company  in companies:
        preds = xdl.loadPrediction(company)
        prices = xdl.loadStockPrice(company)
        grades = pd.DataFrame(columns=['COMPANY','MONTH','PREDNO','ESTIMID','ALYSNAM','GRADE'])

        totalPred = len(preds)
        for i, row in preds.iterrows():
            val, date = grade(preds, prices, grades, i)
            if val != -1:
                grades.loc[len(grades)] = [row['XCOMPANY'],date,0,row['ESTIMID'],row['ALYSNAM'],val]
            else:
                preds.set_value(i, 'GRADE', val)
            xit.progressRatio(len(grades), totalPred, "Pred analysis", 2)



        analyst_grades = preds[["ESTIMID", "GRADE"]]
        analyst_grades = grades.groupby(['ESTIMID']).mean()
        print(analyst_grades)
        print(grades)


