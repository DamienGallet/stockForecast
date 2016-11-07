from dataLoader import pred_path,price_path,split_path,cached_path,data_file_main_path
import os
from os import listdir


def cleanDir(directory, targetExt=".csv"):
    files = listdir(directory)
    for file in files:
        if targetExt in file:
            os.remove(os.path.join(directory, file))


def clearCache():
    cacheDir = data_file_main_path+cached_path
    directoriesToClean = [cacheDir+pred_path, cacheDir+price_path]
    for directory in directoriesToClean:
        cleanDir(directory)


def clearSplit():
    splitDir = data_file_main_path+split_path
    directoriesToClean = [splitDir+pred_path, splitDir+price_path]
    for directory in directoriesToClean:
        cleanDir(directory)

