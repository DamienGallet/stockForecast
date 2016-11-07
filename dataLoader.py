import pandas as pd
import numpy as np
from datetime import timedelta
from datetime import datetime
import os.path


data_file_main_path = "data/"
pred_path = "pred/"
price_path = "price/"
cached_path = "cached/"
split_path = "split/"

ENCODING_TYPE = "ISO-8859-1"

class DataType:
    PRED = "pred/"
    PRICE = "price/"
    FORECAST = "forecast/"
    GRADES = "grades/"

def getCachePath(company, type):

    return data_file_main_path + cached_path + type + company + ".csv"

def getFilePath(company, type):

    return data_file_main_path + split_path + type + company + ".csv"

def getFromCache(company, type):
    path = getCachePath(company, type)
    if os.path.isfile(path):
        print("Get from cache "+path)
        return pd.read_csv(path)
    else:
        return

def putToFile(company, type, db):
    path = getFilePath(company, type)
    print("Store file "+path)
    db.to_csv(path,index=False)

def putToCache(company, type, db):
    path = getCachePath(company, type)
    print("Store cache "+path)
    db.to_csv(path,index=False)

def writePandaInCSV(db,path):
    db.to_csv(path,index=False)

def date_to_month(date):
    delta_year = date.year - 1900
    month = date.month
    return delta_year * 12 + month

# param
#   +path : string
def loadPrediction(company, split=True):
    """

    :type company: str
    :rtype: DataFrame
    """
    if split:
        path = data_file_main_path+split_path+pred_path+company+'.csv'
    else:
        path = data_file_main_path+pred_path+company+'.csv'

    print('Loading of predictions in '+path)
    if split:
        data = pd.read_csv(path,encoding=ENCODING_TYPE)
    else:
        data = pd.read_csv(path,parse_dates=[['ACTDATS', 'ACTTIMS']],encoding=ENCODING_TYPE)
        data['MONTH'] = data.apply (lambda row: date_to_month(row['ACTDATS_ACTTIMS']),axis=1)
    data['XCOMPANY'] = company
    data = cleanColumns(data,[])
    return data

def loadStockPrice(company, split=True):
    """

    :type company: str
    :rtype: DataFrame
    """
    if split:
        path = data_file_main_path+split_path+price_path+company+'.csv'
    else:
        path = data_file_main_path+price_path+company+'.csv'

    print('Loading of prices in '+path)
    if split:
        data = pd.read_csv(path,parse_dates=['DATE'],encoding=ENCODING_TYPE)
    else:
        data = pd.read_csv(path,encoding=ENCODING_TYPE)
        data['DATE'] = pd.to_datetime(data['date'],format="%Y%m%d")

    data['MONTH'] = data.apply (lambda row: date_to_month(row['DATE']),axis=1)
    data['XCOMPANY'] = company
    data.set_index(['MONTH'],inplace=True)
    if not split:
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

