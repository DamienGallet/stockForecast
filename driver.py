import dataLoader as xdl
import interface as xit
import numpy as np
from datetime import timedelta
import pandas as pd
import ploting_utilities


companiesA = [
            "IBM",
            "MSFT",
            "INTC",
            "XOM",
            "WMT",
            "NYX",
            "ABX",
            "BA",
            "KO",
            "DD",
            "MCD",
            "GS"]

companies = ['SNDK',
'DVN',
'INTC',
'SLB',
'QCOM',
'CLR',
'JPM',
'BP',

"IBM",
            "MSFT",
            "INTC",
            "XOM",
            "WMT",
            "NYX",
            "ABX",
            "BA",
            "KO",
            "DD",
            "MCD",
            "GS"]


def grade(preds, prices, i):

    currentPred = preds.loc[i]

    value, date = getRealPrice(currentPred, prices)
    if value == -1:
        return -1, 0

    pred = currentPred['VALUE']
    finalGrade = absoluteGradeFun(pred, value)
    return finalGrade, date


def getRealPrice(pred, prices):

    horizon = pred['HORIZON']
    crtMnth = pred['MONTH']
    forecastMonth = crtMnth+horizon

    try:
        line = prices.loc[forecastMonth]
    except:
        return -1, 0

    if len(line) == 0:
        line = prices.loc[crtMnth+horizon:crtMnth+horizon+3]
        goodLine = line.head(1)
        forecastMonth = goodLine.index.item()
    else:
        goodLine = line
    if len(line) == 0:
        return -1, 0

    return goodLine['PRC'].item(), forecastMonth


def gauss_function(x, a, x0, sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))

def indicatrice_function(current, expected):
    if current == expected:
        return 1
    return 0.01

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


def absoluteGradeFun(forecastValue, finalPrice):
    if forecastValue == finalPrice:
        return 1

    if forecastValue < finalPrice:
        return forecastValue/finalPrice
    return finalPrice/forecastValue


def getPriceFromHorizon(init_date, horizon, prices):
    start_date = init_date + timedelta(days=horizon*30-31)
    end_date = init_date + timedelta(days=horizon*30)
    mask = (prices['DATE'] > start_date) & (prices['DATE'] <= end_date)
    return prices.loc[mask]


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


def getMergedGrades(allGrades, newGrades):

    if allGrades is None:
        return newGrades
    else:
        return allGrades.append(newGrades)


def plotCompany(prices, preds, grades, forecast, company):
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


def main(refresh=False, store=True):

    allGrades = None
    for company in companies:
        #try:
        preds = xdl.loadPrediction(company)
        prices = xdl.loadStockPrice(company)

        grades = getGrades(company, preds, prices, refresh, store)

        forecast = price_forecast(grades, company)
        forecast = evaluateForecast(forecast, prices)
        xdl.putToCache(company, xdl.DataType.FORECAST, forecast)

        allGrades = getMergedGrades(allGrades, grades)

        plotCompany(prices, preds, grades, forecast, company)
        '''except:
            print('------------------------------')
            print('ERROR for the company '+company)
            print('------------------------------')'''


    grades_c = allGrades[["ESTIMID", "GRADE"]]
    analyst_grades = grades_c.groupby(['ESTIMID']).agg(['mean', 'count', 'std'])

    xdl.putToCache("ALL",xdl.DataType.GRADES,analyst_grades)

    print(analyst_grades)
    ploting_utilities.pause()


def test():
    x1 = [10, 11, 12, 13]
    y1 = [100, 101, 102, 103]
    x2 = [11, 12, 13, 14]
    y2 = [101, 102, 103, 104]

    ploting_utilities.plots2D([x1, x2], [y1, y2])


def dataSplitter(name="bulkedB"):
    preds = xdl.loadPrediction(name, False)
    prices = xdl.loadStockPrice(name, False)
    onlyCompanies = preds[['OFTIC']]
    detectedCompanies = onlyCompanies.groupby(['OFTIC']).groups

    for company in detectedCompanies.keys():

        maskPred = (preds['OFTIC'] == company)
        maskPrice = (prices['TICKER'] == company)
        predsCompany = preds.loc[maskPred]
        priceCompany = prices.loc[maskPrice]
        xdl.putToFile(company, xdl.DataType.PRED, predsCompany)
        xdl.putToFile(company, xdl.DataType.PRICE, priceCompany)




if __name__ == "__main__":
    main()
