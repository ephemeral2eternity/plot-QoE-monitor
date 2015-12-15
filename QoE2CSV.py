# Convert user chunk QoE trace file to csv format
# Chen Wang
# chenw@andrew.cmu.edu
# QoE2CSV.py
import json
import datetime
import csv
import glob
import re
import ntpath
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

## ==================================================================================================
# Converting chunk QoE traces from json files ot CSV files
# @input : inputFolder --- the input folder of client chunk QoE json files.
# 		   outputFolder --- the output folder of client chunk QoE traces in CSV format.
## ==================================================================================================
def qoe2csv(inputFolder, outputFolder):
	## Get user QoE files
	qoe_files = glob.glob(inputFolder + "*")

	sqs = {}

	## Process each user QoE file
	for user_qoe_file in qoe_files:
		user_file_name = ntpath.basename(user_qoe_file)
		user_csv_file_name = outputFolder + user_file_name.replace('json', 'csv')
		f = open(user_csv_file_name, 'wb')
		user_qoes = json.load(open(user_qoe_file))
		for chunk in sorted(user_qoes.keys(), key=int):
			chunk_srv = user_qoes[chunk]['Server']
			chunk_TS = user_qoes[chunk]['TS']
			chunk_QoE = user_qoes[chunk]['QoE']
			chunk_buf = user_qoes[chunk]['Buffer']
			chunk_freezing = user_qoes[chunk]['Freezing']
			chunk_rep = user_qoes[chunk]['Representation']
			chunk_response = user_qoes[chunk]['Response']

			f.write(str(chunk) + ", " + str(chunk_QoE) + ", " + str(chunk_buf) + ", " + str(chunk_freezing) + ", " + \
				 str(chunk_rep) + str(chunk_response) + str(chunk_TS) + "\n")

		print "Finish converting file for: ", user_file_name	
		f.close()

## ==================================================================================================
# Main testing script
## ==================================================================================================
inputFolder = "/Users/Chen/code/python/plot-QoE-monitor/fastly-qoe-1103/"
outputFolder = "/Users/Chen/code/python/plot-QoE-monitor/fastly-qoe-csv-1103/"
qoe2csv(inputFolder, outputFolder)
