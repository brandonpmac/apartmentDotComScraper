import requests
import json
from bs4 import BeautifulSoup


class Apartment():
    """Generates an object with data parsed from an inputed link"""

    def __init__(self,link,classPointerFilepath) -> None:

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

        # Defining the all the variables found in the script.
        self.name              = self.find_data('Name')             # Apartment Name
        self.address           = self.find_data('Address')          # Apartment Street address
        self.city              = self.find_data('City')             # Apartment City
        self.state             = self.find_data('State')            # Apartment State
        self.zip               = self.find_data('Zip')              # Apartment Zip
        self.neighboorhood     = self.find_data('Neighboorhood')    # Neighboorhood
        self.rating            = self.find_data('Review Rating')    # Rating from Apartments.com
        self.number_of_reviews = self.find_data('Num of Reviews')   # Number of Reviews 

        # Special Formating for specific variables
        self.name = self.name.split(' - ')[0].replace('\t','')

        # Formating found data into new varibales
        self.full_address =  f'{self.address}, {self.city}, {self.state} {self.zip}'  

        
        #####################
        # LISTINGS
        #####################

        # First find all occurances of a listing in the scraped data.  
        # Then iterate through all occurances to scrape data from html.  
        # Append them to the the data
        #

        # Finds all occurances of a listing in the scrapped data.
        self.raw_listings = []
        self.listings = {}
        listing_indicies = [i for i, line in enumerate(self.data) if line.__contains__(self.pointers['Listing'][0])]
        
        # Defining the keys to search for in each listing
        listing_keys = [
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
            new_listing = {}
            for key in listing_keys:
                new_listing[key] = self.find_data(key,line)
            
            model_name = new_listing['Model Name']
            if model_name in self.listings:
                self.listings[model_name]['Listings'].append(
                    {
                        'Units'           : new_listing['Unit Number'],
                        'Rent'            : new_listing['Rent'],
                        'Date Availible'  : new_listing['Date Availible']
                    }
                )
            else:
                self.listings[model_name] = {
                    # Assuming the number of beds, baths, and area will be the same
                    'Number of Beds'  : new_listing['Number of Beds'],
                    'Number of Baths' : new_listing['Number of Baths'],
                    'Area'            : new_listing['Area'],
                    'Listings'        : [{
                        'Units'           : new_listing['Unit Number'],
                        'Rent'            : new_listing['Rent'],
                        'Date Availible'  : new_listing['Date Availible']
                    }]
                }
                

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

