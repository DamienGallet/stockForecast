import pandas as pd
import numpy as np
from datetime import timedelta
from datetime import datetime

data_file_main_path = "data/"
pred_path = "pred/"
price_path = "price/"

def writePandaInCSV(db,path):
    db.to_csv(path,index=False)

def date_to_month(date):
    delta_year = date.year - 1900
    month = date.month
    return delta_year * 12 + month

# param
#   +path : string
def loadPrediction(company):
    """

    :type company: str
    :rtype: DataFrame
    """
    path = data_file_main_path+pred_path+company+'.csv'
    data = pd.read_csv(path,parse_dates=[['ACTDATS', 'ACTTIMS']])
    data['MONTH'] = data.apply (lambda row: date_to_month(row['ACTDATS_ACTTIMS']),axis=1)
    data['XCOMPANY'] = company
    data = cleanColumns(data,[])
    return data

def loadStockPrice(company):
    """

    :type company: str
    :rtype: DataFrame
    """
    path = data_file_main_path+price_path+company+'.csv'
    data = pd.read_csv(path)
    data['XCOMPANY'] = company
    data['DATE'] = pd.to_datetime(data['date'],format="%Y%m%d")
    data['MONTH'] = data.apply (lambda row: date_to_month(row['DATE']),axis=1)
    data.set_index(['MONTH'],inplace=True)
    print(data)
    data = cleanColumns(data,['date'])
    return data

def cleanColumns(db, columnsToDrop):
    """

    :rtype: object
    """
    for column in columnsToDrop:
        db.drop(column,axis=1,inplace=True)
    return db


def giveInfoOnDB(db):
    # Lines
    print(str(len(db)) + " lines in this database")

    # Columns
    cols_name = list(db.columns.values)
    print(str(len(cols_name)) + " Columns :")
    for col_name in cols_name:
        print(col_name)

def uniformize(db):
    return db

