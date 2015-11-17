# Plot chunk QoE values, or moving average of chunk QoE values, or exponential smoothing chunk QoE values over time on one server.
# Chen Wang, chenw@andrew.cmu.edu
# plot_SQS.py
import glob
import json
import datetime
import ntpath
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

## ==================================================================================================
# Given a Server QoE Score file in json format, plot the SQS (monitored by chunk QoE from all users
# streaming from the server ) over time.
# @input : dataFile --- the input SQS file in json format
# 		   plt_sty --- the line style to plot.
#		   pltMode --- could be "srv" or "method"; 
#						"srv" will have the legend of the server ip;
#						"method" will show the legend as "Chunk QoE"
# @return: the server ip
## ==================================================================================================
def plot_chunk_qoes(dataFile, plt_sty, pltMode):
	file_name = ntpath.basename(dataFile)
	srv_ip = file_name.split('_')[0]
	srv_chunk_qoe = json.load(open(dataFile))

	## Choose the label according to pltMode
	if pltMode is 'srv':
		labelStr = srv_ip
	elif pltMode is 'method':
		labelStr = 'Chunk QoE'

	# Plot the chunk QoE curves over time
	ts = [x for x in srv_chunk_qoe.keys()]
	sorted_ts = sorted(ts, key=float)

	chunk_qoes = [srv_chunk_qoe[cur_ts]['QoE'] for cur_ts in sorted_ts]
	plt.plot(sorted_ts, chunk_qoes, plt_sty, label=labelStr, linewidth=2.0, markersize=8)

	return srv_ip, chunk_qoes

## ==================================================================================================
# Given a Server QoE Score file in json format, plot the SQS (moving average of chunk QoE monitored 
# from all users streaming from the server ) over time.
# @input : dataFile --- the input SQS file in json format
#		   W --- the window size of moving average
# 		   plt_sty --- the line style to plot.
#		   pltMode --- could be "srv" or "method"; 
#						"srv" will have the legend of the server ip;
#						"method" will show the legend as "Moving Average with W = $W"
# @return: the server ip
## ==================================================================================================
def plot_moving_average_sqs(dataFile, W, plt_sty, pltMode):
	file_name = ntpath.basename(dataFile)
	srv_ip = file_name.split('_')[0]
	srv_chunk_qoe = json.load(open(dataFile))

	## Choose the label according to pltMode
	if pltMode is 'srv':
		labelStr = srv_ip
		print srv_ip
	elif pltMode is 'method':
		labelStr = 'Moving Average W = ' + str(W)

	# Plot the chunk QoE curves over time
	ts = [x for x in srv_chunk_qoe.keys()]
	sorted_ts = sorted(ts, key=float)

	chunk_qoes = [srv_chunk_qoe[cur_ts]['QoE'] for cur_ts in sorted_ts]
	N = len(chunk_qoes)

	ma_sqs = chunk_qoes[:]
	for i in range(N):
		if i < W:
			ma_sqs[i] = sum(chunk_qoes[:i])/float(i+1)
		else:
			ma_sqs[i] = sum(chunk_qoes[i - (W - 1) : i]) / float(W)

	plt.plot(sorted_ts, ma_sqs, plt_sty, label=labelStr, linewidth=2.0, markersize=8)

	return srv_ip, ma_sqs

## ==================================================================================================
# Given a Server QoE Score file in json format, plot the SQS (exponential smoothing of chunk QoE monitored 
# from all users streaming from the server ) over time.
# @input : dataFile --- the input SQS file in json format
#		   alpha --- the parameter of exponential smoothing x_t = x_{t-1} * (1 - alpha) + s_t * alpha
# 		   plt_sty --- the line style to plot.
#		   pltMode --- could be "srv" or "method"; 
#						"srv" will have the legend of the server ip;
#						"method" will show the legend as "Exponential smoothing alpha = $alpha"
# @return: the server ip
## ==================================================================================================
def plot_exp_smoothing_sqs(dataFile, alpha, plt_sty, pltMode):
	file_name = ntpath.basename(dataFile)
	srv_ip = file_name.split('_')[0]
	srv_chunk_qoe = json.load(open(dataFile))

	## Choose the label according to pltMode
	if pltMode is 'srv':
		labelStr = srv_ip
	elif pltMode is 'method':
		labelStr = 'Exponential Smoothing $\\alpha$ = ' + str(alpha)

	# Plot the chunk QoE curves over time
	ts = [x for x in srv_chunk_qoe.keys()]
	sorted_ts = sorted(ts, key=float)

	chunk_qoes = [srv_chunk_qoe[cur_ts]['QoE'] for cur_ts in sorted_ts]

	exp_sqs = []
	exp_sqs.append(chunk_qoes[0])

	for qoe in chunk_qoes[1:]:
		cur_sqs = (1 - alpha) * exp_sqs[-1] + alpha * qoe
		exp_sqs.append(cur_sqs)

	plt.plot(sorted_ts, exp_sqs, plt_sty, label=labelStr, linewidth=2.0, markersize=5)
	return srv_ip, exp_sqs

## ==================================================================================================
# Draw chunk QoE over time for multiple servers.
## ==================================================================================================
dataFolder = "/Users/Chen/code/python/plot-QoE-monitor/azure/azure-sqs-json-1116/"
dataLabel = "Azure1116"
srv_files = glob.glob(dataFolder + "*.json")
plt_styles = ['b-', 'k-v', 'r-x', 'm->', 'y-s', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d', 'y-<', 'g-o', 'b-8']
ln_styles = ['b-', 'k-.', 'r--', 'm:', 'y-', 'g-.', 'b--', 'k:', 'r-', 'm-.', 'y--', 'g:', 'b-+']

## The full interval of all servers
# ts_interval = [1446577200, 1446578700]

# Fastly 1103 10 minute interval
# ts_interval = [1446577200, 1446577800]

# Azure1116 10 minutes
ts_interval = [1447687800, 1447688400]

'''
figNo = 0
fig, ax = plt.subplots()
pltMode = "srv"
alpha = 0.2

all_srv_sqs = {}
for dataFile in srv_files:
	srv_ip, srv_sqs = plot_exp_smoothing_sqs(dataFile, alpha, ln_styles[figNo], pltMode)
	all_srv_sqs[srv_ip] = srv_sqs
	figNo = figNo + 1

## Change the time stamp ticks
num_intvs = int((ts_interval[-1] - ts_interval[0])/60) + 1
ts_labels = [ts_interval[0] + x*60 for x in range(num_intvs)]
str_ts = [datetime.datetime.fromtimestamp(x*60 + ts_interval[0]).strftime('%H:%M') for x in range(num_intvs)]
plt.xticks(ts_labels, str_ts, fontsize=15)

box = ax.get_position()

ax.set_xlabel("Time in a day", fontsize=20)
ax.set_ylabel("Server QoE Score (0-5)", fontsize=20)
ax.set_xlim(ts_interval)
ax.set_ylim([0,5])

ax.set_position([box.x0, box.y0 + 0.1, box.width, box.height * 0.9])
ax.legend(bbox_to_anchor=(1.0, 0.9), fancybox=True, shadow=True, ncol=1, prop={'size':15})
params = {'legend.fontsize': 15, 'legend.linewidth': 2}
plt.rcParams.update(params)
ax.set_title('Chunk QoE monitored from users on all servers', fontsize=20) 
plt.show()

pdf = PdfPages('./imgs/' + dataLabel + '_EXP_SQS.pdf')
pdf.savefig(fig)
pdf.close()

srv_sqs_mn = {}
srv_sqs_std = {}
for server in all_srv_sqs.keys():
	srv_sqs_mn[server] = np.mean(all_srv_sqs[server])
	srv_sqs_std[server] = np.std(all_srv_sqs[server])

## Plot the bar chart
sorted_srvs = sorted(srv_sqs_mn.keys(), key=srv_sqs_mn.get, reverse=True)
sorted_srv_mn = [srv_sqs_mn[s] for s in sorted_srvs]
sorted_srv_std = [srv_sqs_std[s] for s in sorted_srvs]
fig, ax = plt.subplots()
ind = np.arange(len(sorted_srvs))
width = 0.35
rects = ax.bar(ind + width, sorted_srv_mn, width, color='y', yerr=sorted_srv_std)

# add some text for labels, title and axes ticks
ax.set_ylabel('Server QoE Score (0-5) Mean and STD')
ax.set_xticks(ind + width)
ax.set_xticklabels(sorted_srvs)
fig.autofmt_xdate()

plt.show()

pdf = PdfPages('./imgs/' + dataLabel + '_SQS_Bar_on_Servers.pdf')
pdf.savefig(fig)
pdf.close()

'''
'''
## ==================================================================================================
# Compare methods of SQS on one server including chunk QoE, moving average and smooth streaming
## ==================================================================================================
cur_file = srv_files[2]
fig, ax = plt.subplots()
pltMode = "method"
W = 10
alpha = 0.2
plot_chunk_qoes(cur_file, plt_styles[0], pltMode)
plot_moving_average_sqs(cur_file, W, plt_styles[1], pltMode)
srv_ip, _ = plot_exp_smoothing_sqs(cur_file, alpha, plt_styles[2], pltMode)

## Change the time stamp ticks
num_intvs = int((ts_interval[-1] - ts_interval[0])/60) + 1
ts_labels = [ts_interval[0] + x*60 for x in range(num_intvs)]
str_ts = [datetime.datetime.fromtimestamp(x*60 + ts_interval[0]).strftime('%H:%M') for x in range(num_intvs)]
plt.xticks(ts_labels, str_ts, fontsize=15)

box = ax.get_position()

ax.set_xlabel("Time in a day", fontsize=20)
ax.set_ylabel("Server QoE Score (0-5)", fontsize=20)
ax.set_ylim([0,5])
ax.set_xlim(ts_interval)

ax.set_position([box.x0, box.y0 + 0.1, box.width, box.height * 0.9])
ax.legend(bbox_to_anchor=(1, 0.9), fancybox=True, shadow=True, ncol=1, prop={'size':15})
params = {'legend.fontsize': 15, 'legend.linewidth': 2}
plt.rcParams.update(params)
ax.set_title('SQS generated using various methods on server ' + srv_ip, fontsize=20) 
plt.show()

pdf = PdfPages('./imgs/' + srv_ip + '_SQS.pdf')
pdf.savefig(fig)
pdf.close()

'''

'''
## ==================================================================================================
# Compare SQS on one server using moving average with various window size 
## ==================================================================================================
cur_file = srv_files[0]
fig, ax = plt.subplots()
pltMode = "method"
W = 10
plot_chunk_qoes(cur_file, plt_styles[0], pltMode)
plot_moving_average_sqs(cur_file, 5, plt_styles[1], pltMode)
plot_moving_average_sqs(cur_file, 10, plt_styles[2], pltMode)
srv_ip = plot_moving_average_sqs(cur_file, 20, plt_styles[3], pltMode)
srv_ip = plot_moving_average_sqs(cur_file, 40, plt_styles[4], pltMode)

## Change the time stamp ticks
num_intvs = int((ts_interval[-1] - ts_interval[0])/60) + 1
ts_labels = [ts_interval[0] + x*60 for x in range(num_intvs)]
str_ts = [datetime.datetime.fromtimestamp(x*60 + ts_interval[0]).strftime('%H:%M') for x in range(num_intvs)]
plt.xticks(ts_labels, str_ts, fontsize=15)

box = ax.get_position()

ax.set_xlabel("Time in a day", fontsize=20)
ax.set_ylabel("Server QoE Score (0-5)", fontsize=20)
ax.set_ylim([0,5])

ax.set_position([box.x0, box.y0 + 0.1, box.width, box.height * 0.9])
ax.legend(bbox_to_anchor=(1, 0), fancybox=True, shadow=True, ncol=1, prop={'size':15})
params = {'legend.fontsize': 15, 'legend.linewidth': 2}
plt.rcParams.update(params)
ax.set_title('SQS generated using various methods on server ' + srv_ip, fontsize=20) 
plt.show()

pdf = PdfPages('./imgs/' + srv_ip + '_MA_SQS.pdf')
pdf.savefig(fig)
pdf.close()
'''

'''
## ==================================================================================================
# Compare SQS on one server using exponential smoothing with various parameters. 
## ==================================================================================================
cur_file = srv_files[0]
fig, ax = plt.subplots()
pltMode = "method"
W = 10
plot_chunk_qoes(cur_file, plt_styles[0], pltMode)
srv_ip = plot_exp_smoothing_sqs(cur_file, 0.4, plt_styles[3], pltMode)
plot_exp_smoothing_sqs(cur_file, 0.2, plt_styles[2], pltMode)
plot_exp_smoothing_sqs(cur_file, 0.1, plt_styles[1], pltMode)

## Change the time stamp ticks
num_intvs = int((ts_interval[-1] - ts_interval[0])/60) + 1
ts_labels = [ts_interval[0] + x*60 for x in range(num_intvs)]
str_ts = [datetime.datetime.fromtimestamp(x*60 + ts_interval[0]).strftime('%H:%M') for x in range(num_intvs)]
plt.xticks(ts_labels, str_ts, fontsize=15)

box = ax.get_position()

ax.set_xlabel("Time in a day", fontsize=20)
ax.set_ylabel("Server QoE Score (0-5)", fontsize=20)
ax.set_ylim([0,5])

ax.set_position([box.x0, box.y0 + 0.1, box.width, box.height * 0.9])
ax.legend(bbox_to_anchor=(1, 0), fancybox=True, shadow=True, ncol=1, prop={'size':15})
params = {'legend.fontsize': 15, 'legend.linewidth': 2}
plt.rcParams.update(params)
ax.set_title('SQS generated using various methods on server ' + srv_ip, fontsize=20) 
plt.show()

pdf = PdfPages('./imgs/' + srv_ip + '_EXP_SQS.pdf')
pdf.savefig(fig)
pdf.close()
'''