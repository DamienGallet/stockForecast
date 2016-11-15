import dataLoader as xdl
import interface as xit
import numpy as np
from datetime import timedelta
import pandas as pd
import ploting_utilities
import relative as rel
from utilities import *
from absolute import *
from relative import *
from shortTerm import *


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

companiesV = ['MCD','ABX']

def main(refresh=False, store=True):

    allGrades = None
    for company in companies:
        #try:
        preds = xdl.loadPrediction(company)
        prices = xdl.loadStockPrice(company)

        computeAndPlotShort(prices, preds, company)
        '''(forecast, grades, allGrades) = absoluteForecast(company,
                                                         preds,
                                                         prices,
                                                         refresh,
                                                         store,
                                                         allGrades)

        plotAbsolute(prices, preds, grades, forecast, company)
        companyS = [company]
        (analystGrades, preds, forecastFAll) = relativeForecast(preds, prices,companies)

        plotRelative(prices, preds, preds, forecastFAll[company], company)

        except:
            print('------------------------------')
            print('ERROR for the company '+company)
            print('------------------------------')'''


    '''grades_c = allGrades[["ESTIMID", "GRADE"]]
    analyst_grades = grades_c.groupby(['ESTIMID']).agg(['mean', 'count', 'std'])

    xdl.putToCache("ALL",xdl.DataType.GRADES,analyst_grades)'''

    #print(analystGrades)
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
