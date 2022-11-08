import argparse
import urllib.parse
import urllib.request
import os
import math
import re
import requests
from datetime import datetime
import json

def main():
    # ############### INITIALIZATION ###############

    # Getting arguments
    args = getArguments()

    # Assigning args to variables
    inputLink =         args.link
    removeLink =        args.remove
    newSharedPath =      args.setup
    updateApartments =  args.update
    writeToExcel =      args.write

    # Defining fileLoactions Path and opening to retrieve data
    fileLocationsFilepath = os.path.abspath('./programData/fileLocations.json')
    checkFilePath(fileLocationsFilepath,'./programData')

    # Opening fileLocations.json to retrieve the data
    with open(fileLocationsFilepath,'r') as f:
        fileLocationsData = json.load(f)

    # Detecting if setup was called - This is done first so that the user can continue with the program 
    if newSharedPath != None:
        # Formating the path and checking if it exists
        updatedPath = os.path.abspath(newSharedPath)
        checkFilePath(updatedPath)

        # Updating fileLocationsData with correct filepath
        fileLocationsData['sharedDirrPath'] = updatedPath

        # writing the new data to fileLocations.json
        with open(fileLocationsFilepath,'w') as f:
            json.dump(fileLocationsData,f,indent=4)

    
    # ############### FILEPATHS ###############

    # Defining Shared Filepaths
    sharedDir = os.path.abspath(fileLocationsData['sharedDirPath'])
    apartmentLinksFilepath = os.path.join(sharedDir,fileLocationsData['apartmentLinksFilepath'])
    apartmentsDataFilepath = os.path.join(sharedDir,fileLocationsData['apartmentsDataFilepath'])

    # Checking Shared Filepaths
    checkFilePath(sharedDir)
    checkFilePath(apartmentLinksFilepath)
    checkFilePath(apartmentsDataFilepath)


    # ############### ACTIONS ###############
    # ---------- Args.link ----------
    if args.link != None:
        # Getting the existing links from file
        with open(apartmentLinksFilepath) as f:    
                existingLinks = f.readlines()

        # Checking to see if the link is valid
        #   - If not, raise an exception
        parsedLink = urllib.parse.urlparse(inputLink)       # Parsing the link to get the network location
        if parsedLink.netloc != 'www.apartments.com':       # If the link is not located at apartments.com, raise an exception
            raise Exception('Error, incompatable link')

        # Checking to see if the input link is in the existing links
        #   - If not, append to existing links file
        if inputLink not in existingLinks:
            with open(apartmentLinksFilepath,'a') as f:
                f.writelines(''.join([inputLink,'\n']))

    # ---------- Args.update ----------
    if args.update == 'yes':
        updateSheet()
    
# ############### FUNCTIONS ################

# Function returns command line arguments
def getArguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Scrapes an apartment.com linkt to add data to a file.')

    # ---------- Command Line Arguments ----------
    # -l, --link:   Link command line argument
    parser.add_argument(
        '-l',   
        '--link',
        type=str,                   # Input type
        required=False,             # Making optional
        help='Adds link to apartmentLinks.txt and appends data to apartmentsData.json'
        )

    # -r, --remove: Remove command line argument
    parser.add_argument(
        '-r',
        '--remove',
        type=str,                   # Input type
        required=False,             # Making options
        help='Removes the included links from the program.'
        )

    # -s, --setup:  Setup command line argument
    parser.add_argument(
        '-s',
        '--setup',
        type=str,
        required=False,
        help='Argument that specifies the shared folder path. Only nessescary to run when first installing the program.'
        )

    # -u, --update: Update command line argument
    parser.add_argument(
        '-u',
        '--update',
        action='store_true',        # Defining the type of argument
        required=False,             # Setting to optional
        default=False,              # Setting the default value to False
        help='Update apartmentData.json with links in apartmentLinks.txt.'
        )

    # -w, --write:  Write command line argument
    parser.add_argument(
        '-w',
        '--write',
        action='store_true',        # Defining the type of argument
        required=False,             # Setting to optional
        default=False,              # Setting the default value to False
        help='Writes the current apratmentsData.json to and output excel file.'
        )
    
    return parser.parse_args()

def scrapeLink(link) -> dict:
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

def checkFilePath(filePath,fileDir='None'):
    convertedFilePath = os.path.abspath(filePath)   # Converting the path to absolute path
    fileName = os.path.split(convertedFilePath)[1]  # Getting the file name from converted path

    # Formating the error message depending upon input
    if fileDir != 'None':
        errorPrompt = f'Error, {fileName} not found. Please ensure that file is located in {fileDir}'
    else:
        errorPrompt = f'Error, {fileName} not found.'
    
    # Checking to see if the file exists
    if not os.path.exists(convertedFilePath):
        raise FileNotFoundError(errorPrompt)
    


def updateSheet():
    pass

if __name__ == "__main__":
    main()