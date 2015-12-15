# Convert user chunk QoE trace file to per server QoE file in csv file.
# Chen Wang, chenw@andrew.cmu.edu
# QoE2SQS.py
import json
import datetime
import csv
import glob
import re
import ntpath
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

## ==================================================================================================
# Converting chunk QoE json traces to the server QoE score traces in CSV format
# @input : inputFolder --- the input folder of client chunk QoE json files.
# 		   outputFolder --- the output folder of the Server QoE Score (SQS) trace files in CSV format
## ==================================================================================================
def qoe2sqs_csv(inputFolder, outputFolder):
	## Get user QoE files
	qoe_files = glob.glob(inputFolder + "*")

	sqs = {}

	## Process each user QoE file
	for user_qoe_file in qoe_files:
		user_file_name = ntpath.basename(user_qoe_file)
		user_name = user_file_name.split('_')[0]
		user_qoes = json.load(open(user_qoe_file))
		for chunk in sorted(user_qoes.keys(), key=int):
			chunk_srv = user_qoes[chunk]['Server']
			chunk_TS = user_qoes[chunk]['TS']
			chunk_QoE = user_qoes[chunk]['QoE']
			chunk_buf = user_qoes[chunk]['Buffer']
			chunk_freezing = user_qoes[chunk]['Freezing']
			chunk_rep = user_qoes[chunk]['Representation']
			chunk_response = user_qoes[chunk]['Response']
			if chunk_srv in sqs.keys():
				sqs[chunk_srv][chunk_TS] = [chunk_QoE, chunk_buf, chunk_freezing, chunk_response, user_name, chunk, chunk_rep]
			else:
				sqs[chunk_srv] = {}
				sqs[chunk_srv][chunk_TS] = [chunk_QoE, chunk_buf, chunk_freezing, chunk_response, user_name, chunk, chunk_rep]

		print user_name

	for srv in sqs.keys():
		outputFileName = outputFolder + srv + "_sqs.csv"
		f = open(outputFileName, 'wb')
		for ts in sorted(sqs[srv].keys(), key=int):
			row = ", ".join(str(x) for x in sqs[srv][ts])
			f.write(str(ts) + ", " + row + "\n")
		f.close()

## ==================================================================================================
# Converting chunk QoE json traces to the server QoE score traces in json format
# @input : inputFolder --- the input folder of client chunk QoE json files.
# 		   outputFolder --- the output folder of the Server QoE Score (SQS) trace files in JSON format
## ==================================================================================================
def qoe2sqs_json(inputFolder, outputFolder):
	## Get user QoE files
	qoe_files = glob.glob(inputFolder + "*")

	sqs = {}

	## Process each user QoE file
	for user_qoe_file in qoe_files:
		user_file_name = ntpath.basename(user_qoe_file)
		user_name = user_file_name.split('_')[0]
		user_qoes = json.load(open(user_qoe_file))
		for chunk in sorted(user_qoes.keys(), key=int):
			chunk_srv = user_qoes[chunk]['Server']
			chunk_TS = user_qoes[chunk]['TS']
			if chunk_srv in sqs.keys():
				sqs[chunk_srv][chunk_TS] = {'QoE' : user_qoes[chunk]['QoE'], 'User' : user_name, "ChunkID" : chunk,  'Representation' : user_qoes[chunk]['Representation'], 'Buffer' : user_qoes[chunk]['Buffer'], 'Freezing' : user_qoes[chunk]['Freezing'], 'Response' : user_qoes[chunk]['Response']}
			else:
				sqs[chunk_srv] = {}
				sqs[chunk_srv][chunk_TS] = {'QoE' : user_qoes[chunk]['QoE'], 'User' : user_name, "ChunkID" : chunk,  'Representation' : user_qoes[chunk]['Representation'], 'Buffer' : user_qoes[chunk]['Buffer'], 'Freezing' : user_qoes[chunk]['Freezing'], 'Response' : user_qoes[chunk]['Response']}

		print user_name

	for srv in sqs.keys():
		outputFileName = outputFolder + srv + "_sqs.json"
		with open(outputFileName, 'w') as outfile:
			json.dump(sqs[srv], outfile, sort_keys = True, indent = 4, ensure_ascii=False)


## ==================================================================================================
# Main testing script
## ==================================================================================================
inputFolder = "/Users/Chen/code/python/plot-QoE-monitor/azure/azure-qoe-1116/"
outputFolder = "/Users/Chen/code/python/plot-QoE-monitor/azure/azure-sqs-json-1116/"
qoe2sqs_json(inputFolder, outputFolder)
