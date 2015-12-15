from geopy.geocoders import Nominatim

## Read Azure location file and generate coordinates for All Azure locations
def load_azure_loc():
	## Read the azure-loc.csv file to draw the planetlab node locations
	azure_loc = {}
	with open('data/azure-loc.csv', 'rU') as csvfile:
		csvreader = csv.reader(csvfile, delimiter=',')
		for row in csvreader:
			region = row[0]
			loc = row[1]
			azure_loc[loc] = region

	return azure_loc


geolocator = Nominatim()
azure_locs = load_azure_loc()

for loc in azure_locs.keys():
    location = geolocator.geocode(loc)
print((location.latitude, location.longitude))