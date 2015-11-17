# Save all user information to file.
# Chen Wang, chenw@andrew.cmu.edu
# get_users.py
import glob
import json
import datetime
import ntpath
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

## Default data folder
inputFolder = '/Users/Chen/code/python/plot-QoE-monitor/azure/azure-qoe-1116/'
outputFolder = '/Users/Chen/code/python/plot-QoE-monitor/data/'

## Get user QoE files
qoe_files = glob.glob(inputFolder + "*")

users = []

## Process each user QoE file
for user_qoe_file in qoe_files:
	user_file_name = ntpath.basename(user_qoe_file)
	user_name = user_file_name.split('_')[0]
	users.append(user_name)

## Write the list of users to csv file
user_file_name = outputFolder + 'users.csv'
with open(user_file_name, 'wb') as f:
    writer = csv.writer(f)
    for val in users:
        writer.writerow([val])
