# Plot chunk QoE values, or moving average of chunk QoE values, or exponential smoothing chunk QoE values over time on one server.
# Chen Wang, chenw@andrew.cmu.edu
# compare_SQS_on_users.py
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
# Draw SQS bar with average and std on users
# @input : sqs_file_name --- the input SQS file in json format
# @return: the server ip
## ==================================================================================================
def sqs_bar_on_users(sqs_file_name, domains):
	file_name = ntpath.basename(sqs_file_name)
	srv_ip = file_name.split('_')[0]
	srv_chunk_qoe = json.load(open(sqs_file_name))

	## Organize QoE under each user
	client_qoes = {}
	client_qoes_mn = {}
	client_qoes_std = {}

	for ts in sorted(srv_chunk_qoe.keys(), key=float):
		cur_client = srv_chunk_qoe[ts]['User']
		if cur_client not in client_qoes.keys():
			client_qoes[cur_client] = {}
			client_qoes[cur_client][ts] = srv_chunk_qoe[ts]['QoE']
		else:
			client_qoes[cur_client][ts] = srv_chunk_qoe[ts]['QoE']

	for client in client_qoes.keys():
		client_qoes_mn[client] = np.mean(client_qoes[client].values())
		client_qoes_std[client] = np.std(client_qoes[client].values())

	## Count the mean and deviation of QoEs under each user.
	sorted_clients = sorted(client_qoes_mn.keys(), key=client_qoes_mn.get, reverse=True)
	clt_qoes_mn = [client_qoes_mn[clt] for clt in sorted_clients]
	clt_qoes_std = [client_qoes_std[clt] for clt in sorted_clients]
	domain_colors = {'Europe' : 'r', 'America' : 'b', 'Asia' : 'y', 'Australia' : 'm', 'Unknown' : 'k'}
	client_colors = ''
	client_regions = []
	for client in sorted_clients:
		client_domain = client.split('.')[-1]
		client_region = search_domain_region(client_domain, domains)
		if client_region not in client_regions:
			client_regions.append(client_region)
		client_colors = client_colors + domain_colors[client_region]

	## Plot the bar chart
	fig, ax = plt.subplots()
	ind = np.arange(len(sorted_clients))
	width = 0.35
	rects = ax.bar(ind + width, clt_qoes_mn, width, color=client_colors, yerr=clt_qoes_std)

	# add some text for labels, title and axes ticks
	ax.set_ylabel('User chunk QoE (0-5) mean (std)')
	ax.set_title('QoE on users streaming from server ' + srv_ip)
	ax.set_xticks(ind + width)
	ax.set_xticklabels(sorted_clients)
	fig.autofmt_xdate()

	## Add legend for regions
	patches = []
	for region in client_regions:
		patches.append(mpatches.Patch(color=domain_colors[region], label=region))

	plt.figlegend(patches, client_regions, loc=0)

	plt.show()

	pdf = PdfPages('./imgs/' + srv_ip + '_SQS_Bar_on_Users.pdf')
	pdf.savefig(fig)
	pdf.close()

## ==================================================================================================
# Draw SQS curves on users
# @input : sqs_file_name --- the input SQS file in json format
# @return: the server ip
## ==================================================================================================
def sqs_curve_on_users(sqs_file_name, SLA):
	file_name = ntpath.basename(sqs_file_name)
	srv_ip = file_name.split('_')[0]
	srv_chunk_qoe = json.load(open(sqs_file_name))

	## Organize QoE under each user
	client_qoes = {}

	for ts in sorted(srv_chunk_qoe.keys(), key=float):
		cur_client = srv_chunk_qoe[ts]['User']
		if cur_client not in client_qoes.keys():
			client_qoes[cur_client] = {}
			client_qoes[cur_client][ts] = srv_chunk_qoe[ts]['QoE']
		else:
			client_qoes[cur_client][ts] = srv_chunk_qoe[ts]['QoE']
	
	## Select clients having QoE below SLA
	nomal_clients = []
	anomaly_clients = []
	plt_styles = ['k-v', 'r-x', 'm->', 'y-s', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d', 'y-<', 'g-o', 'b-8']

	## Plot the bar chart
	normal_qoe_dict = {}
	fig, ax = plt.subplots()
	for client in client_qoes.keys():
		if all(qoe > SLA for qoe in client_qoes[client].values()):
			nomal_clients.append(client)
			normal_qoe_dict.update(client_qoes[client])
		else:
			anomaly_clients.append(client)
			cur_qoes_dict = client_qoes[client]
			cur_ts = sorted(cur_qoes_dict.keys(), key=float)
			cur_qoes = [cur_qoes_dict[ts] for ts in cur_ts]
			plt.plot(cur_ts, cur_qoes, plt_styles[anomaly_clients.index(client)], label=client, linewidth=2.0, markersize=8)

	normal_client_ts = sorted(normal_qoe_dict.keys(), key=float)
	normal_client_qoes = [normal_qoe_dict[ts] for ts in normal_client_ts]
	plt.plot(normal_client_ts, normal_client_qoes, 'b-', label='Nomal Client', linewidth=1.0)

	# add some text for labels, title and axes ticks
	ax.set_ylabel('User Chunk QoE (0-5)')
	ax.set_xlabel('Time')
	ax.set_ylim([0,5])
	ax.set_title('QoE on users streaming from server ' + srv_ip)
	

	## Change the time stamp ticks
	# 10 minute interval
	#ts_interval = [1446577200, 1446578100]

	# Azure1116 10 minutes
	ts_interval = [1447687800, 1447688400]
	num_intvs = int((ts_interval[-1] - ts_interval[0])/60) + 1
	ts_labels = [ts_interval[0] + x*60 for x in range(num_intvs)]
	str_ts = [datetime.datetime.fromtimestamp(x*60 + ts_interval[0]).strftime('%H:%M') for x in range(num_intvs)]
	plt.xticks(ts_labels, str_ts, fontsize=15)
	ax.set_xlim(ts_interval)

	plt.legend(loc=0)

	plt.show()

	pdf = PdfPages('./imgs/' + srv_ip + '_SLA_1_0.pdf')
	pdf.savefig(fig)
	pdf.close()


## ==================================================================================================
# Search the region of a client via its domain name.
# @input : client_domain: the suffix of the client domain name
# @return: the name of the continent the client belongs to.
## ==================================================================================================
def search_domain_region(client_domain, domains):
	for region in domains.keys():
		if client_domain in domains[region]:
			return region

	return "Unknown"

## ==================================================================================================
# Draw chunk QoE over time for multiple servers.
## ==================================================================================================
dataFolder = "/Users/Chen/code/python/plot-QoE-monitor/azure/azure-sqs-json-1116/"
dataLabel = "Azure1116"
srv_files = glob.glob(dataFolder + "*.json")
# plt_styles = ['k-v', 'b-8', 'r-x', 'm->', 'y-s', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d', 'y-<', 'g-o']

domains = {'Europe': ['pl', 'dk', 'es', 'pt', 'uk', 'fr', 'it', 'gr', 'cz', 'de', 'fi', 'se', 'be', 'ie', 'ch'],
		   'America': ['edu', 'ca', 'br', 'ec', 'us'],
		   'Asia': ['cn', 'kr', 'jp', 'hk', 'sg', 'th'],
		   'Australia': ['nz', 'au']}

## The full interval of all servers
# ts_interval = [1446577200, 1446578700]

cur_file = srv_files[1]
sqs_bar_on_users(cur_file, domains)
# SLA = 1.0
# sqs_curve_on_users(cur_file, SLA)