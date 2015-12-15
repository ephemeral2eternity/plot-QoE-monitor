# Plot users who report QoE below SLA
# chenw@andrew.cmu.edu
# map_abnormal_users.py
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import csv
import ntpath
import glob
import json

def load_node_info():
	## Read the coodinates.csv file to draw the planetlab node locations
	node_dict = {}
	with open('data/nodes.csv', 'rU') as csvfile:
		csvreader = csv.reader(csvfile, delimiter=',')
		for row in csvreader:
			user_name = row[1]
			user_id = row[0]
			site_id = row[2]
			node_dict[user_name] = {'ID' : user_id, 'Site_ID' : site_id}

	return node_dict

def load_coodinates():
	## Read the coodinates.csv file to draw the planetlab node locations
	coords = {}
	with open('data/coordinates.csv', 'rU') as csvfile:
		csvreader = csv.reader(csvfile, delimiter=',')
		for row in csvreader:
			site_id = row[0]
			lat = float(row[2])
			lon = float(row[3])
			coords[site_id] = [lat, lon]
	return coords

def draw_abnormal_users(abnormal_users, normal_users):
	markers = ['s', 'p', 'h', 'D', 'o', 'v', '*', '+', '8', '^', '<', '>', '1', '2', '3', '4']
	colors = ['gray', 'firebrick', 'sienna', 'bisque', 'gold', 'darkred', 'hotpink', 'darkblue', 'green', 'darkslategray', 'skyblue', 'blue', 'slateblue', 'blueviolet']
	user_coords = {}
	node_dict = load_node_info()
	# print node_dict
	coordinates = load_coodinates()
	# print coordinates

	## Initialize the map with robinson projection
	map = Basemap(projection='robin', lat_0=0, lon_0=9.1)
	#vmap.drawcoastlines()
	map.fillcontinents(color='lightsteelblue', lake_color=None)
	srv_id = 0
	for srv in srv_users.keys():
		srv_user_list = srv_users[srv]
		user_id = 0
		for user in srv_user_list:
			user_site_id = node_dict[user]['Site_ID']
			user_coords = coordinates[user_site_id]
			lat = user_coords[0]
			lon = user_coords[1]
			x, y = map(lon, lat)
			if user_id < 1:
				map.plot(x, y, marker=markers[srv_id], fillstyle='full', markersize=5, color=colors[srv_id], label=srv)
			else:
				map.plot(x, y, marker=markers[srv_id], fillstyle='full', markersize=5, color=colors[srv_id])
			user_id += 1

		srv_id += 1

	plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	plt.savefig("imgs/per_srv_users.pdf", bbox_inches="tight")
	plt.show()

## ==================================================================================================
# Detect users having QoE below SLA
# @input : sqs_file_name --- the input SQS file in json format
# @return: the server ip
## ==================================================================================================
def detect_abnormal_users(dataFolder, SLA):
	qoe_files = glob.glob(dataFolder + "*")

	normal_users = []
	abnormal_users = []
	## Process each user QoE file
	for user_qoe_file in qoe_files:
		user_file_name = ntpath.basename(user_qoe_file)
		user_name = user_file_name.split('_')[0]
		user_qoes = json.load(open(user_qoe_file))
		qoe_list = [user_qoes[chunk]['QoE'] for chunk in sorted(user_qoes.keys(), key=int)]

		if all(qoe> SLA for qoe in qoe_list):
			normal_users.append(user_name)
		else:
			abnormal_users.append(user_name)

	return normal_users, abnormal_users

## ==================================================================================================
# Draw normal and abnormal users in a global map
# @input : sqs_file_name --- the input SQS file in json format
# @return: the server ip
## ==================================================================================================
def draw_per_srv_users(normal_users, abnormal_users):
	markers = ['s', 'o']
	colors = ['blue', 'red']
	node_dict = load_node_info()
	# print node_dict
	coordinates = load_coodinates()
	# print coordinates

	## Initialize the map with robinson projection
	map = Basemap(projection='robin', lat_0=0, lon_0=9.1)
	#vmap.drawcoastlines()
	map.fillcontinents(color='lightsteelblue', lake_color=None)
	user_id = 0
	for user in normal_users:
		user_site_id = node_dict[user]['Site_ID']
		user_coords = coordinates[user_site_id]
		lat = user_coords[0]
		lon = user_coords[1]
		x, y = map(lon, lat)
		if user_id < 1:
			map.plot(x, y, marker=markers[0], fillstyle='full', markersize=5, color=colors[0], label="Users meeting SLA")
		else:
			map.plot(x, y, marker=markers[0], fillstyle='full', markersize=5, color=colors[0])
		user_id += 1

	user_id = 0
	for user in abnormal_users:
		user_site_id = node_dict[user]['Site_ID']
		user_coords = coordinates[user_site_id]
		lat = user_coords[0]
		lon = user_coords[1]
		x, y = map(lon, lat)
		if user_id < 1:
			map.plot(x, y, marker=markers[1], fillstyle='full', markersize=5, color=colors[1], label="Users violating SLA")
		else:
			map.plot(x, y, marker=markers[1], fillstyle='full', markersize=8, color=colors[1])
		user_id += 1

	plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	plt.savefig("imgs/map_abnormal_users.pdf", bbox_inches="tight")
	plt.show()
		
## ==================================================================================================
# Draw chunk QoE over time for multiple servers.
## ==================================================================================================
dataFolder = "/Users/Chen/code/python/plot-QoE-monitor/fastly-qoe-1103/"
dataLabel = "Fastly1103"
SLA = 1.0

normal_users, abnormal_users = detect_abnormal_users(dataFolder, SLA)
draw_per_srv_users(normal_users, abnormal_users)

print abnormal_users