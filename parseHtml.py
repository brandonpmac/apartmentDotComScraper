import os
import math
import re
import requests
from datetime import datetime
        
def main():
    parseHtml('https://www.apartments.com/403-west-raleigh-nc/4n6l61k/')

def parseHtml(link) -> dict:
    # Defining the headers for the html request
    HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    }
    # Pulling data from apartments.com
    htmlText = requests.get(link,timeout=5,headers=HEADERS).text    # Getting the html data from apartments.com
    data = htmlText.split('\n')
    
    # Defining the Dictionary for data to be stored
    apartment = {
        'Address' :         '',
        'City' :            '',
        'State':            '',
        'Zip':              '',
        'Latitude':        '',
        'Longitude':        '',
        'Neighboorhood':    '',
        'Rating':           '',
        'Num of Reviews':   '',
        'Listing':          [],
        'Garmin Time':      '',
        'Partners Time':    ''
    }

    # Searching through the data to check for keys
    for i,row in enumerate(data):
        # ----- Parsing Address -----
        # Getting Address and City
        if 'propertyAddressContainer' in row:           
            apartment['Address'] =        formatHtml(data[i+2])               # Address
            apartment['City'] =           formatHtml(data[i+3])               # City

        # Getting the State and Zip Data
        if 'stateZipContainer' in row:
            apartment['State'] =          formatHtml(data[i+1])               # State
            apartment['Zip'] =            formatHtml(data[i+2])               # Zip Code

        # Getting the Neighborhood
        if 'class="neighborhoodAddress"' in row:
            apartment['Neighboorhood'] =  formatHtml(data[i+2]).split('/')    # Neighborhood

        if 'place:location:latitude' in row:
            apartment['Latitude'] = formatListing(data[i])

        if 'place:location:longitude' in row:
            apartment['Longitude'] = formatListing(data[i])

        # Getting the Review Data
        if 'class="reviewRating"' in row:
            apartment['Rating'] =         formatHtml(data[i])                 # Raiting
        if 'class="reviewCount"' in row:
            apartment['Num of Reviews'] = re.sub('\D','',formatHtml(data[i])) # Number of Reviews - Special fomating to only display Int
        
        # Getting the Individual listing data
        if 'class="unitContainer js-unitContainer' in row:
            Listing = {
                'modelName' :     formatListing(data[i+16]),
                'unit' : [{
                    'unitNumber' :    formatListing(data[i+17]),    
                    'rent' :          formatListing(data[i+11]),
                    'dateAvail' :     formatListing(data[i+39])
                }],
                'numberBeds' :    formatListing(data[i+14]),
                'numberBath' :    formatListing(data[i+15]),
                'area' :          formatHtml(data[i+33])
            }
            found = False
            for indiv in apartment['Listing']:
                if Listing['modelName'] == indiv['modelName']:
                    if Listing['unit'][0] not in indiv['unit']:
                        indiv['unit'].append(Listing['unit'][0])
                    found = True
                    break
            if found == False:
                apartment['Listing'].append(Listing)
    
    # Formating for getDirections()
    address = ''.join([
        apartment['Address'],
        ', ',
        apartment['City'],
        ', ',
        apartment['State'],
        ' ',
        apartment['Zip']])
    [apartment['Garmin Time'],apartment['Partners Time']] = getDirections(
        address,
        apartment['Latitude'],
        apartment['Longitude']
        )
    return apartment

def formatHtml(rawText):
    rawText = rawText.replace('>','<')
    splitText = rawText.split('<')
    text = splitText[math.floor(len(splitText)/2)]
    return text

def formatListing(rawText):
    rawText = rawText.split('=')[-1]
    rawText = rawText.replace('"','')
    rawText = rawText.replace('    ','')
    rawText = rawText.replace('>','')
    rawText = rawText.replace('\r','')
    return rawText
        
def getDirections(address,lat,long):

    coordinates = ''.join(['@',lat,',',long])
    # chromeDriverPath = os.path.abspath('/opt/homebrew/bin/chromedriver')
    garminMapsUrl = ''.join(['https://www.google.com/maps/dir/',address,'/Garmin,+12040+Regency+Pkwy,+Cary,+NC+27518/',coordinates])
    partnersMapUrl = ''.join(['https://www.google.com/maps/dir/',address,'/Partners+Way+Parking+Deck,+Partners+Way,+Raleigh,+NC/',coordinates])
    mapLinks = [garminMapsUrl,partnersMapUrl]

    # Defining time variables to determine travel time
    currentTime = datetime.strptime(datetime.strftime(datetime.now(),"%I:%M %p"),"%I:%M %p")    # Getting the current time without the assiciated year (pardon the weird formating)
    travelTimes = []                                                    # Shortest travel times for Garmin and Partners
    for i, link in enumerate(mapLinks):
        # Defining the header for the html request
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        }
        htmlText = requests.get(link,timeout=10,headers=HEADERS).text   # Getting the html source from google maps for the current route
        data = htmlText.split('\n')                                     # Splitting the html by new line

        timeLocations = [m.start() for m in re.finditer('You should arrive around', data[15])]  # Indecies for where the time data is located
        times = []  # List of all times calculated from google maps
        for loc in timeLocations:
            newTimeStr = data[15][loc+25:loc+33].replace('.','')    # Get the time data from the html code, with formating
            newTime = datetime.strptime(newTimeStr,"%I:%M %p")      # Convert the time date to a time object
            timeDiff = newTime-currentTime                          # Get the time difference between the current time and time data
            times.append(timeDiff.seconds/60)                       # Append the time difference, converting to min and a string
        travelTimes.append(min(times))                              # Appending the shortest time
    return travelTimes                                              # Returning the travel times


if __name__ == "__main__":
    data = main()


