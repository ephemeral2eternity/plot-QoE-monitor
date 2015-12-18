# Plot system performance and server QoE score under various anomaly events
# Chen Wang, chenw@andrew.cmu.edu
# plot_SQS.py
import glob
import json
import time
import datetime
import ntpath
import csv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

## Change string to int or float
def num(num_str):
    try:
        return int(num_str)
    except ValueError:
        return float(num_str)

## Read anomalies from log file.
def getAnomalies(anomalyFile):
    ## Read the coodinates.csv file to draw the planetlab node locations
    anomalies = {}
    with open(anomalyFile, 'rU') as csvfile:
        anomaly_reader = csv.reader(csvfile, delimiter=',')
        headers = anomaly_reader.next()
        print headers
        for row in anomaly_reader:
            print row
            anomaly_ts = row[0]
            anomalies[anomaly_ts] = {}
            for col_id in range(1, len(headers)):
                anomalies[anomaly_ts][headers[col_id]] = row[col_id]
        return anomalies

## Read anomalies from log file.
def getChunkQoE(sqsFil, qoeTyp):
    ## Read the coodinates.csv file to draw the planetlab node locations
    srv_chunk_qoe = json.load(open(sqsFile))
    # Plot the chunk QoE curves over time
    ts = [x for x in srv_chunk_qoe.keys()]
    sorted_ts = sorted(ts, key=float)

    chunk_qoes = {}
    for cur_ts in sorted_ts:
        chunk_qoes[cur_ts] = srv_chunk_qoe[cur_ts][qoeTyp]
    return chunk_qoes

def compute_sqs(chunk_qoes, ave_method, params):
    if (ave_method is not 'MA') and (ave_method is not 'EXP'):
        print "The method to compute does not exists so we use expAve to smooth the SQS!"
        ave_method = 'EXP'

    sorted_ts = sorted(chunk_qoes.keys(), key=float)
    qoe_list = [chunk_qoes[cur_ts] for cur_ts in sorted_ts]

    sqs = {}
    if ave_method is 'MA':
        W = params
        ma_sqs = chunk_qoes[:]
        for i in range(len(sorted_ts)):
            if i < W:
                sqs[sorted_ts[i]] = sum(qoe_list[:i])/float(i+1)
            else:
                sqs[sorted_ts[i]] = sum(qoe_list[i - (W - 1) : i]) / float(W)
    else:
        alpha = params
        sqs_list = []
        sqs_list.append(qoe_list[0])
        sqs[sorted_ts[0]] = sqs_list[0]
        ts_id = 1
        for qoe in qoe_list[1:]:
            next_sqs = (1 - alpha) * sqs_list[-1] + alpha * qoe
            sqs_list.append(next_sqs)
            sqs[sorted_ts[ts_id]] = sqs_list[ts_id]
            ts_id += 1
    return sqs

def utc_mktime(utc_tuple):
    """
    Returns number of seconds elapsed since epoch
    Note that no timezone are taken into consideration.
    utc tuple must be: (year, month, day, hour, minute, second)
    """
    if len(utc_tuple) == 6:
        utc_tuple += (0, 0, 0)
    return time.mktime(utc_tuple) - time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))

def datetime_to_timestamp(dt):
    """
    Converts a datetime object to UTC timestamp
    """
    return float(utc_mktime(dt.timetuple()))

def read_sys_metrics(sysMetricFolder, metric_file_typs):
    ## Read the coodinates.csv file to draw the planetlab node locations
    sys_metrics = {}
    for metric_typ in metric_file_typs:
        with open(sysMetricFolder + metric_typ + '.csv', 'rU') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            headers = csv_reader.next()
            units = csv_reader.next()
            row_to_skip = csv_reader.next()
            for metric_id in range(1, len(headers)):
                metric_name = headers[metric_id]
                sys_metrics[metric_name] = {}
                sys_metrics[metric_name]['unit'] = units[metric_id]
                sys_metrics[metric_name]['data'] = {}

            for row in csv_reader:
                cur_time = datetime.datetime.strptime(row[0], "%a %b %d %H:%M:%S")
                actual_time = cur_time.replace(year=2015)
                cur_ts = datetime_to_timestamp(actual_time)

                for metric_id in range(1, len(headers)):
                    metric_name = headers[metric_id]
                    sys_metrics[metric_name]['data'][cur_ts] = num(row[metric_id])

    return sys_metrics

def draw_anomaly(ax, metricName, anomaly_intvl, anomaly_typ, anomaly_params, sqs_intvl):
        ## Plot Server QoE Scores
    time_win = 60
    label_win = 20

    ## update plot time interval
    plot_intvl = []
    plot_intvl.append(max(anomaly_intvl[0] - time_win, sqs_intvl[0]))
    plot_intvl.append(min(anomaly_intvl[1] + time_win, sqs_intvl[1]))
    plt.axvspan(anomaly_intvl[0], anomaly_intvl[1], facecolor='r', alpha=0.4)

    ## update timestamp labels
    num_intvs = int((plot_intvl[-1] - plot_intvl[0])/label_win) + 1
    ts_labels = [plot_intvl[0] + x*label_win for x in range(num_intvs)]
    str_ts = [datetime.datetime.fromtimestamp(x*label_win + plot_intvl[0]).strftime('%H:%M') for x in range(num_intvs)]
    plt.xticks(ts_labels, str_ts, fontsize=10)

    ax.set_xlim(plot_intvl)
    ax.set_title(metricName + " under \"" + anomaly_typ + "\" anomaly with params: " + anomaly_params, fontsize=15)
    plt.show()

def plot_sqs(ax, sqs):
    ## Plot Server QoE Scores
    sorted_ts = sorted(sqs.keys(), key=float)
    sqs_vals = [sqs[cur_ts] for cur_ts in sorted_ts]
    plt.plot(sorted_ts, sqs_vals, '-b', linewidth=2.0, markersize=5)

    ax.set_xlabel("Time", fontsize=15)
    ax.set_ylabel("Server QoE Score (0 ~ 5)", fontsize=15)

def save_fig(fig, metricName, anomalyName):
    if '[' in metricName:
        fileMetricName = metricName.split('[')[0]
    else:
        fileMetricName = metricName

    dataLabel = fileMetricName.replace('.', '-') + "-" + anomalyName
    pdf = PdfPages('./imgs/' + dataLabel + '.pdf')
    pdf.savefig(fig)
    pdf.close()

def plot_single_metric(ax, sys_metrics, metricName):
    ## Plot CPU utilization
    # metricName = 'kernel.all.load["1 minute"]'
    metricUnit = sys_metrics[metricName]['unit']
    metrics = sys_metrics[metricName]['data']

    sorted_ts = sorted(metrics.keys(), key=float)
    sorted_vals = [metrics[cur_ts] for cur_ts in sorted_ts]

    plt.plot(sorted_ts, sorted_vals, '-b', linewidth=2.0, markersize=5)

    ax.set_xlabel("Time", fontsize=15)
    ax.set_ylabel(metricName + "(" + metricUnit + ")", fontsize=15)

## Main program to plot anomalies with SQS
dataFolder = "D://Data/cloud-monitor-data/anomaly-1216/"
sysMetricFolder = dataFolder + "sys-metrics/"
anomalyFile = dataFolder + "anomaly.csv"
anomalies = getAnomalies(anomalyFile)
sqsFile = dataFolder + "sqs.json"
chunk_qoes = getChunkQoE(sqsFile, 'QoE')
sqs = compute_sqs(chunk_qoes, 'EXP', 0.2)
sqs_intvl = [float(min(sqs.keys(), key=float)), float(max(sqs.keys(), key=float))]
print sqs_intvl
## Read all available system metrics
metric_file_typs = ['cpu', 'io', 'mem', 'mem-faults', 'network', 'tcp']
sys_metrics = read_sys_metrics(sysMetricFolder, metric_file_typs)
for anomaly_ts in anomalies.keys():
    anomaly_intvl = [float(anomaly_ts), float(anomaly_ts) + float(anomalies[anomaly_ts]["Duration"])]
    if (anomaly_intvl[0] > sqs_intvl[0]) and (anomaly_intvl[1] < sqs_intvl[1]):
        anomaly_typ = anomalies[anomaly_ts]['Type']
        anomaly_params = anomalies[anomaly_ts]['Params']

        ## Single Metric plot server load
        metric_to_plot = 'kernel.all.load["1 minute"]'
        fig, ax = plt.subplots()
        plot_single_metric(ax, sys_metrics, metric_to_plot)
        draw_anomaly(ax, metric_to_plot, anomaly_intvl, anomaly_typ, anomaly_params, sqs_intvl)
        save_fig(fig, metric_to_plot, anomaly_typ)

        ## Single Metric plot server load
        metric_to_plot = 'network.tcp.retranssegs'
        fig, ax = plt.subplots()
        plot_single_metric(ax, sys_metrics, metric_to_plot)
        draw_anomaly(ax, metric_to_plot, anomaly_intvl, anomaly_typ, anomaly_params, sqs_intvl)
        save_fig(fig, metric_to_plot, anomaly_typ)

        ## Single Metric plot server load
        metric_to_plot = 'disk.dev.avactive["sda"]'
        fig, ax = plt.subplots()
        plot_single_metric(ax, sys_metrics, metric_to_plot)
        draw_anomaly(ax, metric_to_plot, anomaly_intvl, anomaly_typ, anomaly_params, sqs_intvl)
        save_fig(fig, metric_to_plot, anomaly_typ)

        ## Single Metric plot server load
        metric_to_plot = 'mem.vmstat.pgfault'
        fig, ax = plt.subplots()
        plot_single_metric(ax, sys_metrics, metric_to_plot)
        draw_anomaly(ax, metric_to_plot, anomaly_intvl, anomaly_typ, anomaly_params, sqs_intvl)
        save_fig(fig, metric_to_plot, anomaly_typ)

        ## Server QoE Score plot
        fig, ax = plt.subplots()
        plot_sqs(ax, sqs)
        draw_anomaly(ax, "SQS", anomaly_intvl, anomaly_typ, anomaly_params, sqs_intvl)
        save_fig(fig, "SQS", anomaly_typ)