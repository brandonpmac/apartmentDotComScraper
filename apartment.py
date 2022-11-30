import requests
import json
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import math

class Apartment():
    """Generates an object with data parsed from an inputed link
    
    Functions:
        __init__():

        returnData():
    """


    def __init__(self,link,classPointerFilepath) -> None:
        """Generates an object with data parsed from an inputed link"""
        # Defining the apartment link
        self.link = link

        # Getting apartmentClassPointers
        with open(classPointerFilepath,'r') as f:
            self.pointers = json.load(f)
        
        # Getting the data to parse through from website
        self.data = self.scrape_link(self.link)

        #####################
        # APARTMENT DATA
        #####################   

        # Defining the address
        self.name              = self.find_data('Name').split(' - ')[0].replace('\t','')
        self.address           = self.find_data('Address')
        self.city              = self.find_data('City')
        self.state             = self.find_data('State')
        self.zip               = self.find_data('Zip')
        self.neighboorhood     = self.find_data('Neighboorhood')
        self.latitude          = self.find_data('Latitude')
        self.longitude         = self.find_data('Longitude')
        self.rating            = self.find_data('Review Rating')
        self.number_of_reviews = self.find_data('Num of Reviews')
        # self.travel_times      = {}

        # Formating found data into new varibales
        self.full_address =  f'{self.address}, {self.city}, {self.state} {self.zip}'  


        #####################
        # TRAVEL TIMES
        #####################

        # current_time = datetime.strptime(datetime.strftime(datetime.now(),"%I:%M %p"),"%I:%M %p")

        # for i,address in enumerate(self.pointers['Travel Addresses']):
        #     if i >=1:
        #         formatted_address = address.replace(' ','+')
        #         travel_link = '/'.join([
        #             'https://www.google.com/maps/dir',
        #             self.address.replace(' ','+'),
        #             formatted_address
        #         ])
                
        #         travel_data = self.scrape_link(travel_link)
        #         time_locations = [m.start() for m in re.finditer(self.pointers['Travel Addresses'][0], travel_data[15])]
                
        #         found_times = []

        #         for found_time in time_locations:
        #             new_time_string = travel_data[15][found_time+25:found_time+33]
        #             new_time_string = new_time_string.replace('.','')
        #             new_time = datetime.strptime(new_time_string,"%I:%M %p")
        #             time_difference = new_time-current_time
        #             found_times.append(time_difference.seconds/60)
                
        #         self.travel_times[self.pointers['Travel Names'][i]] = min(found_times)
        #         time.sleep(5)

        
        

        #####################
        # LISTINGS
        #####################

        # Finds all occurances of a listing in the scrapped data.
        self.listings = []
        listing_indicies = [i for i, line in enumerate(self.data) if line.__contains__(self.pointers['Listing'][0])]
        
        # Defining the keys to search for in each listing
        return_keys = [
            'Model Name',
            'Unit Number',
            'Rent',
            'Date Availible',
            'Number of Beds',
            'Number of Baths',
            'Area'
        ]

        # Getting all occurance of a listing and storing the found data in list of dictionaries
        for line in listing_indicies:
            return_data = {}
            for key in return_keys:
                return_data[key] = self.find_data(key,line)
            self.listings.append(return_data)                # Appending the data

        #####################
        # CLEANUP
        #####################

        # Getting rid of the data cause I don't want it stored in the class
        del self.data
        del self.pointers

        

    def scrape_link(self,link):
        """Gets the data from apartments.com using an inputed link."""
         # Defining the headers for the html request
        HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        }
        # Pulling data from apartments.com
        htmlText = requests.get(link,timeout=5,headers=HEADERS).text    # Getting the html data from apartments.com
        return htmlText.split('\n')

    def find_data(self,key,line=0):
        # Defining the flag
        flag = self.pointers[key]

        # create a list of the row of each occurance of the specified pointer in the data
        if len(flag) >> 1:
            position = [i for i,row in enumerate(self.data) if flag[0] in row]
            if len(position) == 1:
                return clean(self.data[position[0]+flag[1]])
        elif len(flag) == 1:
            return clean(self.data[line+flag[0]])

    def return_data(self):
        retrun_dictionary = {
            'Name'          : self.name,
            'Address'       : self.full_address,
            'Neighboorhood' : self.neighboorhood,
            'Rating'        : self.rating,
            'Reviews'       : self.number_of_reviews,
            'Listings'      : self.listings
        }

        return retrun_dictionary

def clean(rawString):
        """Cleans the data from bad formating"""
        soup = BeautifulSoup(rawString, 'html.parser')
        if soup.find_all() != []:
            return soup.find_all()[0].text
        else:
            splitString = rawString.split('\"')
            final_string = splitString[int(len(splitString)/2+0.5)-1]
            final_string = final_string.replace('\r','')
            final_string = final_string.replace('  ','')
            return final_string

def main():
    apt = Apartment('https://www.apartments.com/the-franklin-at-crossroads-raleigh-nc/h1gzdt2/','/Users/brandonmcclenathan/Library/Mobile Documents/com~apple~CloudDocs/Documents/Code/apartmentScraper - Shared Files/dataFiles/apartmentClassPointer.json')
    print(apt.link)
    with open('./dumped.json','w') as f:
        f.write(json.dumps(apt.__dict__, indent=4))

if __name__ == "__main__":
    main()

