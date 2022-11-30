import argparse
import urllib.parse
import urllib.request
import os
import math
import re
import requests
from datetime import datetime
import json
from apartment import Apartment
import tqdm
import time

def main():
    # ############### INITIALIZATION ###############

    # Getting arguments
    args = getArguments()

    # Assigning args to variables
    inputLink        = args.link
    removeLink       = args.remove
    newSharedPath    = args.setup
    updateApartments = args.update
    writeToExcel     = args.write

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
        fileLocationsData['sharedDirPath'] = updatedPath

        # writing the new data to fileLocations.json
        with open(fileLocationsFilepath,'w') as f:
            json.dump(fileLocationsData,f,indent=4)

    
    # ############### FILEPATHS ###############

    # Defining Shared Filepaths
    sharedDir = os.path.abspath(fileLocationsData['sharedDirPath'])
    apartmentLinksFilepath = os.path.join(sharedDir,fileLocationsData['apartmentLinksFilepath'])
    apartmentsDataFilepath = os.path.join(sharedDir,fileLocationsData['apartmentsDataFilepath'])
    apartmentsClassPointerFilepath = os.path.join(sharedDir,fileLocationsData['apartmentsClassPointerPath'])

    # Checking Shared Filepaths
    checkFilePath(sharedDir)
    checkFilePath(apartmentLinksFilepath)
    checkFilePath(apartmentsDataFilepath)
    checkFilePath(apartmentsClassPointerFilepath)

    # ############### ACTIONS ###############

    # ---------- Args.link ----------
    if inputLink != None:
        # Getting the existing links from file
        with open(apartmentLinksFilepath) as f:    
            existing_links = f.readlines()
        
        # Removing \n from the string
        for i,link in enumerate(existing_links):
            existing_links[i] = link.replace('\n','')

        # Checking to see if the link is valid
        #   - If not, raise an exception
        parsedLink = urllib.parse.urlparse(inputLink)       # Parsing the link to get the network location
        if parsedLink.netloc != 'www.apartments.com':       # If the link is not located at apartments.com, raise an exception
            raise Exception('Error, incompatable link')

        # Checking to see if the input link is in the existing links
        #   - If not, append to existing links file
        if inputLink not in existing_links:
            with open(apartmentLinksFilepath,'a') as f:
                f.writelines(''.join([inputLink,'\n']))
            
            new_apartment = Apartment(inputLink,apartmentsClassPointerFilepath)

            with open(apartmentsDataFilepath,'r') as f:
                previous_data = json.load(f)

            previous_data.append(new_apartment.return_data())

            with open(apartmentsDataFilepath,'w') as f:
                json.dump(previous_data,f,indent=4)   # Printing Data to json
            print('\nLink was succesfully added.\n')
        else:
            print('\nLink was already entered into the program.\n')

    # ---------- Args.update ----------
    if updateApartments == True:
        # Getting the existing links from file
        with open(apartmentLinksFilepath) as f:    
            existing_links = f.readlines()
        
        # Removing \n from the string
        for i,link in enumerate(existing_links):
            existing_links[i] = link.replace('\n','')
        
        # Iteration
        update_data = []
        print()
        print('Updating Links')
        for i in tqdm.trange(len(existing_links)):
            # Only sleeping if not the first request
            if i>=1:
                time.sleep(2)

            current_link = existing_links[i]
            current_apartment = Apartment(current_link,apartmentsClassPointerFilepath)

            update_data.append(current_apartment.return_data())
        
        with open(apartmentsDataFilepath,'w') as f:
            json.dump(update_data,f,indent=4)
        
        print()
        print('Apartments successfully updated.\n')

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

if __name__ == "__main__":
    main()