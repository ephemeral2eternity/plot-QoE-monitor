# Plot users on each server on a world map, use different marker to denote different servers.
# Chen Wang
# chenw@andrew.cmu.edu
# map_per_srv_users.py
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

def draw_per_srv_users(srv_users):
	markers = ['s', 'p', 'h', 'D', 'o', 'v', '*', '+', '8', '^', '<', '>', '1', '2', '3', '4']
	colors = ['gray', 'firebrick', 'gold', 'sienna', 'bisque', 'darkred', 'hotpink', 'darkblue', 'green', 'darkslategray', 'skyblue', 'blue', 'slateblue', 'blueviolet']
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

def get_per_srv_users(dataFolder):
	srv_users = {}
	srv_files = glob.glob(dataFolder + "*.json")
	for dataFile in srv_files:
		file_name = ntpath.basename(dataFile)
		srv_ip = file_name.split('_')[0]
		srv_chunk_qoe = json.load(open(dataFile))
		users = [srv_chunk_qoe[str(cur_ts)]['User'] for cur_ts in srv_chunk_qoe.keys()]
		unique_users = list(set(users))
		srv_users[srv_ip] = unique_users

	return srv_users
		

## ==================================================================================================
# Draw chunk QoE over time for multiple servers.
## ==================================================================================================
dataFolder = "/Users/Chen/code/python/plot-QoE-monitor/azure/azure-sqs-json-1116/"
dataLabel = "azure1116"

srv_users = get_per_srv_users(dataFolder)
draw_per_srv_users(srv_users)