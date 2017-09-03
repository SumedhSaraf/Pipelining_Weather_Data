import csv
import time
import datetime 
from datetime import datetime
#get_ipython().magic('matplotlib inline')
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime,date,timedelta
import matplotlib as plt
import logging
import requests
import urllib
import json
import http
import io
from urllib.request import urlopen
from boto.s3.connection import S3Connection
from boto.s3.key import Key

log_file_name = "logger" + ".log"
logger = logging.getLogger(log_file_name)
hdlr = logging.FileHandler(log_file_name)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

with open('configWrangle.json') as data_file:    
        data1 = json.load(data_file)
present_link = data1['rawData'] 
file_name = 'TX_170617_WBAN_13910.csv'

logger.info("The data is being cleaned.....")
print("The data is being cleaned....")

response_new = requests.get(present_link)
dirty_data = pd.read_csv(io.StringIO(response_new.content.decode('utf-8')), low_memory=False,index_col=None)
dirty_data['HOURLYDRYBULBTEMPF'] = pd.to_numeric(dirty_data['HOURLYDRYBULBTEMPF'], errors='coerce')
dirty_data['HOURLYDRYBULBTEMPC'] = pd.to_numeric(dirty_data['HOURLYDRYBULBTEMPC'], errors='coerce')
cols = ['HOURLYDRYBULBTEMPF', 'HOURLYDRYBULBTEMPC']
dirty_data[cols] = dirty_data[cols].ffill()
dirty_data['HOURLYSKYCONDITIONS'] = dirty_data['HOURLYSKYCONDITIONS'].ffill() 
dirty_data['HOURLYVISIBILITY'] = dirty_data['HOURLYVISIBILITY'].ffill() 
dirty_data['REPORTTPYE'] = dirty_data['REPORTTPYE'].ffill() 
dirty_data['HOURLYPRSENTWEATHERTYPE'] = dirty_data['HOURLYPRSENTWEATHERTYPE'].ffill()  
dirty_data['HOURLYPRSENTWEATHERTYPE'] = dirty_data['HOURLYPRSENTWEATHERTYPE'][:96].bfill() 
dirty_data['HOURLYWETBULBTEMPF'] = dirty_data['HOURLYWETBULBTEMPF'].fillna(0)
dirty_data['HOURLYWETBULBTEMPC'] = dirty_data['HOURLYWETBULBTEMPC'].fillna(0)
cols1=['HOURLYDewPointTempF','HOURLYDewPointTempC','HOURLYRelativeHumidity','HOURLYWindSpeed','HOURLYWindDirection']
dirty_data[cols1] = dirty_data[cols1].ffill()
dirty_data['HOURLYWindGustSpeed'] =dirty_data['HOURLYWindGustSpeed'].interpolate()
cols2=['HOURLYStationPressure','HOURLYPressureTendency','HOURLYPressureChange']
dirty_data[cols2] = dirty_data[cols2].bfill()
dirty_data.update(dirty_data[['HOURLYPrecip','HOURLYAltimeterSetting','DAILYDeptFromNormalAverageTemp','DAILYAverageRelativeHumidity','DAILYAverageDewPointTemp','DAILYAverageWetBulbTemp']
].fillna(0))
cols3=['DAILYMaximumDryBulbTemp','DAILYMinimumDryBulbTemp','DAILYAverageDryBulbTemp','DAILYHeatingDegreeDays','DAILYCoolingDegreeDays']
dirty_data[cols3] = dirty_data[cols3].bfill()
dirty_data.update(dirty_data[['DAILYPrecip','DAILYSnowfall','DAILYSnowDepth','DAILYAverageStationPressure','DAILYAverageSeaLevelPressure','DAILYAverageWindSpeed','DAILYPeakWindSpeed','PeakWindDirection','DAILYSustainedWindSpeed','DAILYSustainedWindDirection','MonthlyMaximumTemp','MonthlyMinimumTemp','MonthlyMeanTemp','MonthlyAverageRH','MonthlyDewpointTemp','MonthlyWetBulbTemp','MonthlyAvgHeatingDegreeDays','MonthlyAvgCoolingDegreeDays','MonthlyStationPressure','MonthlySeaLevelPressure','MonthlyAverageWindSpeed','MonthlyTotalSnowfall','MonthlyDeptFromNormalMaximumTemp','MonthlyDeptFromNormalMinimumTemp','MonthlyDeptFromNormalAverageTemp','MonthlyDeptFromNormalPrecip','MonthlyTotalLiquidPrecip','MonthlyGreatestPrecip','MonthlyGreatestPrecipDate','MonthlyGreatestSnowfall','MonthlyGreatestSnowfallDate','MonthlyGreatestSnowDepth','MonthlyGreatestSnowDepthDate','MonthlyDaysWithGT90Temp','MonthlyDaysWithLT32Temp','MonthlyDaysWithGT32Temp','MonthlyDaysWithLT0Temp','MonthlyDaysWithGT001Precip','MonthlyDaysWithGT010Precip','MonthlyDaysWithGT1Snow','MonthlyMaxSeaLevelPressureValue'
]].fillna(0))
dirty_data.to_csv('TX_170617_WBAN_13910_clean.csv',index=False)
logger.info("The data is now clean and stored in csv")
print("The data is now clean and stored in csv")
bucket_name = "cleandatasummerads"
initial_file = "TX_170617_WBAN_13910_clean.csv"
with open('configWrangle.json') as data_file:    
        data1 = json.load(data_file)
conn = S3Connection(data1['AWSAccess'], data1['AWSSecret'])
existingbucket = conn.get_bucket(bucket_name)
existingbucket.set_acl('public-read-write')
initial_data = Key(existingbucket)
initial_data.key = initial_file
initial_data.set_contents_from_filename(initial_file)
logger.info("The clean data is uploaded to S3")
print("The clean data is uploaded to S3")

