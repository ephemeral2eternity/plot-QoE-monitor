import csv
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

user_csv_file_name = 'data/azure-coords.csv'
with open(user_csv_file_name, 'wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')

    loc_id = 1
    for loc in azure_locs.keys():
        location = geolocator.geocode(loc)
        row = [loc_id, loc, azure_locs[loc], location.latitude, location.longitude]
        csvwriter.writerow(row)
        print row
        loc_id = loc_id + 1
