import dataLoader as xdl
from datetime import timedelta
from datetime import datetime
import pandas as pd


companies = ["IBM"]



def grade(prediction, prices,date_max):

    stockValue = -1
    init_hor = prediction['HORIZON'].item()
    horizon = prediction['HORIZON'].item()
    if prediction['ACTDATS_ACTTIMS'] + timedelta(days=horizon*30-31) > date_max:
        return -1

    while stockValue == -1 and horizon - init_hor < 2*init_hor:
        priceLine = getPriceFromHorizon(prediction['ACTDATS_ACTTIMS'], horizon, prices)


        forecastValue = prediction['VALUE'].item()
        if len(priceLine)==0:
            stockValue = -1
            horizon += 1
        else:
            stockValue = priceLine.head(1)['PRC'].item()

    if stockValue == -1:
        return -1

    grade = absoluteGradeFun(forecastValue, stockValue)
    print(grade)
    return grade


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

        #print(prices.between_time(start_time="2008-01-01", end_time="2009-01-01"))
        date_max = prices['DATE'].max()
        for i, row in preds.iterrows():
            val = grade(preds.loc[i], prices, date_max)
            if val == -1:
                preds.drop(i, inplace=True)
            else:
                preds.set_value(i, 'GRADE', val)

        print(preds)
        print(prices)
        analyst_grades = preds[["ESTIMID", "GRADE"]]
        analyst_grades = analyst_grades.groupby(['ESTIMID']).mean()
        print(analyst_grades)


