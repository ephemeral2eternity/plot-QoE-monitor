# Plot cache miss through time on all servers
# Chen Wang, chenw@andrew.cmu.edu
# plot_cache_miss.py
import glob
import json
import datetime
import ntpath
import operator
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

## ==================================================================================================
# Converting chunk QoE json traces to the cache miss on servers
# @input : inputFolder --- the input folder of client chunk QoE json files.
# 		   outputFolder --- the output folder of the cache miss files for all servers in JSON format
## ==================================================================================================
def qoe2cachemiss_json(inputFolder, outputFolder):
	## Get user QoE files
	qoe_files = glob.glob(inputFolder + "*")
	cache_miss_dict = {}
	user_default_srvs = {}
	user_default_redirection_srvs = {}

	## Process each user QoE file
	for user_qoe_file in qoe_files:
		user_file_name = ntpath.basename(user_qoe_file)
		user_name = user_file_name.split('_')[0]
		user_qoes = json.load(open(user_qoe_file))
		default_cache_srv, default_redirection_srv = find_default_cache(user_qoes)
		user_default_srvs[user_name] = default_cache_srv
		user_default_redirection_srvs[user_name] = default_redirection_srv
		print "The default cache server for user : ", user_name, " is ", default_cache_srv

		for chunk in sorted(user_qoes.keys(), key=int):
			chunk_srv = user_qoes[chunk]['Server']
			chunk_TS = user_qoes[chunk]['TS']
			chunk_rep = user_qoes[chunk]['Representation']
			if chunk_srv is not default_cache_srv:
				if chunk_srv in cache_miss_dict.keys():
					cache_miss_dict[chunk_srv][chunk_TS] = {'User' : user_name, 'Chunk' : chunk, 'Representation' : chunk_rep}
				else:
					cache_miss_dict[chunk_srv] = {}
					cache_miss_dict[chunk_srv][chunk_TS] = {'User' : user_name, 'Chunk' : chunk, 'Representation' : chunk_rep}

		for srv in cache_miss_dict.keys():
			outputFileName = outputFolder + srv + "_cachemiss.json"
			with open(outputFileName, 'w') as outfile:
				json.dump(cache_miss_dict[srv], outfile, sort_keys = True, indent = 4, ensure_ascii=False)

	## Print the unique cache server users connect to
	# print list(set(user_default_srvs.values()))
	# print list(set(user_default_redirection_srvs.values()))

## ==================================================================================================
# Find the default cache server that the client is requesting content from.
# @input : user_qoes --- the user chunk QoE trace in json format
# @return : default_cache_srv --- the default cache server the user is selecting.
#			second_redirection_srv --- the default server the user is redirected to.
## ==================================================================================================
def find_default_cache(user_qoes):
	srv_count = {}
	for chunk in sorted(user_qoes.keys(), key=int):
		chunk_srv = user_qoes[chunk]['Server']
		if chunk_srv in srv_count.keys():
			srv_count[chunk_srv] += 1
		else:
			srv_count[chunk_srv] = 1

	sorted_srv_count = sorted(srv_count.items(), key=operator.itemgetter(1), reverse=True)

	if len(sorted_srv_count) > 1:
		return sorted_srv_count[0][0], sorted_srv_count[1][0]
	else:
		return sorted_srv_count[0][0], ''


## ==================================================================================================
# Draw chunk QoE over time for multiple servers.
## ==================================================================================================
inputFolder = "/Users/Chen/code/python/plot-QoE-monitor/fastly-qoe-1103/"
outputFolder = "/Users/Chen/code/python/plot-QoE-monitor/fastly-cachemiss-1103/"
srv_files = glob.glob(inputFolder + "*.json")
# plt_styles = ['k-v', 'b-8', 'r-x', 'm->', 'y-s', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d', 'y-<', 'g-o']

qoe2cachemiss_json(inputFolder, outputFolder)

'''

domains = {'Europe': ['pl', 'dk', 'es', 'pt', 'uk', 'fr', 'it', 'gr', 'cz', 'de', 'fi', 'se', 'be', 'ie', 'ch'],
		   'America': ['edu', 'ca', 'br', 'ec', 'us'],
		   'Asia': ['cn', 'kr', 'jp', 'hk', 'sg', 'th'],
		   'Australia': ['nz', 'au']}

## The full interval of all servers
# ts_interval = [1446577200, 1446578700]

cur_file = srv_files[12]
# sqs_bar_on_users(cur_file, domains)
SLA = 1.0
sqs_curve_on_users(cur_file, SLA)

'''