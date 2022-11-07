import os
from bs4 import BeautifulSoup
import math

def main():
    with open(os.path.abspath('./403Data.html'),'r') as f:
        rawData = f.read()
    parseHtml(rawData)

 
def parseHtml(rawData):
    data = rawData.split('\n')
    listing = {
        "Address" : '',
        'City' :    '',
        'State':    '',
        'Zip':      '',
        'Neighboorhood': ''
    }
    for i,row in enumerate(data):
        # Getting the Address Data
        if 'propertyAddressContainer' in row:           
            listing['Address'] = formatHtml(data[i+2])  # Index into the property address
            listing['City'] = formatHtml(data[i+3])     # Index into the City

        # Getting the State and Zip Data
        if 'stateZipContainer' in row:
            listing['State'] = formatHtml(data[i+1])
            listing['Zip'] = formatHtml(data[i+2])

        # Getting the Neighborhood
        if 'class="neighborhoodAddress"' in row:
            listing['Neighboorhood'] = formatHtml(data[i+2]).split('/')
        



    print(listing)

def formatHtml(rawText):
    rawText = rawText.replace('>','<')
    splitText = rawText.split('<')
    text = splitText[math.floor(len(splitText)/2)]
    return text
        
            
    

    

if __name__ == "__main__":
    data = main()


