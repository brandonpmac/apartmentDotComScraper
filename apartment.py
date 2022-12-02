import requests
import json
from bs4 import BeautifulSoup
import os
import xlsxwriter
from datetime import datetime


class Apartment():
    """Generates an object with data parsed from an inputed link"""

    def __init__(self,link,classPointerFilepath,ignoredListingFilepath) -> None:

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
        if self.rating == '':
            self.rating = float(0)
        self.rating = float(self.rating)
        self.number_of_reviews = int(self.number_of_reviews.replace(' reviews)','').replace('(',''))

        # Formating found data into new varibales
        self.full_address =  f'{self.address}, {self.city}, {self.state} {self.zip}'  

        
        #####################
        # LISTINGS
        #####################

        # First find all occurances of a listing in the scraped data.  
        # Then iterate through all occurances to scrape data from html.  
        # Append them to the the data

        # Finds all occurances of a listing in the scrapped data.
        self.raw_listings = []
        self.listings = []
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

        with open(ignoredListingFilepath,'r') as f:
            ignored_links = json.load(f)

        # Getting all occurance of a listing and storing the found data in list of dictionaries
        for line in listing_indicies:
            new_listing = {}
            for key in listing_keys:
                new_listing[key] = self.find_data(key,line)

            # If no rent was listed
            if new_listing['Rent'] == '':
                new_listing['Rent'] = 0

            model_name = new_listing['Model Name']
            
            cont = True

            for link in ignored_links:
                # If the link is supposed to be ignored
                if link['Floor Plan'] == model_name and link['Apartment'] == self.name: 
                    cont = False
            if cont == True:
                if model_name in [listing['Model Name'] for listing in self.listings]:
                    listing_index = [listing['Model Name'] for listing in self.listings].index(model_name)
                    # Checking to see if exact data is entered
                    existing_listing = self.listings[listing_index]


                    # Checking the existing listings to check if a similar listing exists
                    rent_check = int(new_listing['Rent']) in [unit['Rent'] for unit in existing_listing['Units']]
                    date_check = new_listing['Date Availible'] in [unit['Date Availible'] for unit in existing_listing['Units']]
                    area_check = int(new_listing['Area'].replace(',','')) in [unit['Area'] for unit in existing_listing['Units']]

                    if rent_check and date_check and area_check:
                        pass
                    else:
                        self.listings[listing_index]['Units'].append(
                            {
                                'Unit'            : new_listing['Unit Number'],
                                'Rent'            : int(new_listing['Rent']),
                                'Area'            : int(new_listing['Area'].replace(',','')),
                                'Date Availible'  : new_listing['Date Availible'],
                            }
                        )
                else:
                    self.listings.append(
                        {
                            # Assuming the number of beds, baths, and area will be the same
                            'Model Name'      : model_name,
                            'Number of Beds'  : int(new_listing['Number of Beds']),
                            'Number of Baths' : int(new_listing['Number of Baths']),
                            'Units'        : [{
                            'Unit'            : new_listing['Unit Number'],
                            'Rent'            : int(new_listing['Rent']),
                            'Date Availible'  : new_listing['Date Availible'],
                            'Area'            : int(new_listing['Area'].replace(',','')),
                        }]
                        }
                    )
                

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
        """Returns a dictionary of specified variables."""
        retrun_dictionary = {
            'Name'          : self.name,
            'Address'       : self.full_address,
            'Neighboorhood' : self.neighboorhood,
            'Rating'        : self.rating,
            'Reviews'       : self.number_of_reviews,
            'Listings'      : self.listings,
            'Link'          : self.link
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

def write_to_excel(apartment_filepath,excel_filepath):
    """Writes the apartmentData.json file to a custom excel file."""

    # File Exists Checking
    if not os.path.exists(apartment_filepath):
        raise FileNotFoundError('Apartment Data Filepath not found')
    if not os.path.exists(excel_filepath):
        raise FileNotFoundError('Excel Data Filepath not found')

    # Loading the apartment data
    with open(apartment_filepath,'r') as f:
        apartment_data = json.load(f)
    
    workbook = xlsxwriter.Workbook(excel_filepath)

    #####################
    # DEFINING SHEETS
    #####################
    data_sheet = workbook.add_worksheet('Data')
    # data_sheet = workbook.add_worksheet('Organized Data')
    data_sheet.outline_settings(True,False,False,False)
    

    #####################
    # DEFINING COLORS
    #####################

    # BG Colors
    AH_BLUE         = '#193c64'  # Apartment Header Blue
    LH_BLUE         = '#255fa6'  # Listing Header Blue
    UH_BLUE         = '#8ab5df'  # Unit Header Blue
    VALUE_BLUE      = '#b0cdea'  # Value Blue
    USER_ENTRY_BLUE = '#d5eaf4'  # User Entry Blue


    #####################
    # DEFINING STYLES
    #####################

    # Main Header Format
    apartment_header_format = workbook.add_format({
        'align'    : 'center',
        'bg_color' : AH_BLUE,
        'bold'     : True,
        'color'    : 'white'
    })

    apartment_values_format = workbook.add_format({
        'align'    : 'center',
        'bg_color' : USER_ENTRY_BLUE
    })

    # Apartment Header Format
    listing_header_format = workbook.add_format({
        'align'    : 'center',
        'bg_color' : LH_BLUE,
        'color'    : 'white'
    })

    listing_values_format = workbook.add_format({
        'align'    : 'center',
        'bg_color' : USER_ENTRY_BLUE
    })

    # Listing Header Format
    unit_header_format = workbook.add_format({
        'align'    : 'center',
        'bg_color' : UH_BLUE,
        'color'    : 'white'
    })

    unit_values_format = workbook.add_format({
        'align'    : 'center',
        'bg_color' : USER_ENTRY_BLUE
    })

    money_format = workbook.add_format({
        'num_format': '$#,##0'
    })

    date_format = workbook.add_format({'num_format': 'mm/dd/yy'})
    
    offset = 0

    level_one_start = []
    level_one_end = []
    level_one_range = []

    level_two_start = []
    level_two_end = []
    level_two_range = []

    offset += 1
    for i,apartment in enumerate(apartment_data):
        level_one_start.append(offset)
        for j,listing in enumerate(apartment['Listings']):
            level_two_start.append(offset)
            for k,unit in enumerate(listing['Units']):
                data_sheet.write_string(offset,0,apartment['Name'])
                data_sheet.write_string(offset,1,listing['Model Name'])
                data_sheet.write_number(offset,2,listing['Number of Beds'])
                data_sheet.write_number(offset,3,listing['Number of Baths'])
                data_sheet.write_number(offset,4,unit['Rent'],money_format)
                data_sheet.write_number(offset,5,unit['Rent']/listing['Number of Beds'],money_format)
                if unit['Date Availible'] == 'Now':
                    data_sheet.write_datetime(offset,6,datetime.now(),date_format)
                else:
                    try:
                        data_sheet.write_datetime(offset,6,datetime.strptime(unit['Date Availible'].replace('.',''),'%b %d, %Y'),date_format)
                    except:
                        data_sheet.write_datetime(offset,6,datetime.strptime(''.join([unit['Date Availible'].replace('.',''),', ',datetime.now().strftime("%Y")]),'%b %d, %Y'),date_format)
                data_sheet.write_number(offset,7,unit['Area'])
                data_sheet.write(offset,8,apartment['Neighboorhood'])
                data_sheet.write(offset,9,apartment['Address'])
                data_sheet.write(offset,10,apartment['Link'])

                offset += 1
            level_two_end.append(offset-1)
        level_one_end.append(offset-1)

    # List of Level 2 Range
    for i in range(len(level_one_start)):
        level_one_range.append(range(level_one_start[i],level_one_end[i]))

    # List of Level 1 range
    for i in range(len(level_two_start)):
        level_two_range.append(range(level_two_start[i],level_two_end[i]))
    
    # for i in range(offset+1):
    #     if i in [num for ranges in level_two_range for num in ranges]:
    #         data_sheet.set_row(i,None,None,{'level': 2,'hidden':True})
    #     elif i in [num for ranges in level_one_range for num in ranges]:
    #         data_sheet.set_row(i,None,None,{'level': 1,'hidden':True})

    data_sheet.add_table(0,0,offset-1,10,{'columns': [
        {'header': 'Apartment Name'},
        {'header': 'Floor Plan'},
        {'header': 'Bedrooms'},
        {'header': 'Bathrooms'},
        {'header': 'Price'},
        {'header': 'Price per Bed'},
        {'header': 'Date Availible'},
        {'header': 'Sq Feet'},
        {'header': 'Location'},
        {'header': 'Address'},
        {'header': 'Link'}
        ]})

    # adjusting widths
    data_sheet.set_column(0,0,40)
    data_sheet.set_column(1,1,17)
    data_sheet.set_column(2,2,11)
    data_sheet.set_column(3,3,11)
    data_sheet.set_column(4,4,11)
    data_sheet.set_column(5,5,15)
    data_sheet.set_column(6,6,15)
    data_sheet.set_column(7,7,8.5)
    data_sheet.set_column(8,8,20)
    data_sheet.set_column(9,9,40)
    data_sheet.set_column(10,10,70)

    workbook.close()

def main():
    apt = Apartment('https://www.apartments.com/axis-crossroads-cary-nc/4le0yzj/','/Volumes/GoogleDrive/My Drive/Projects/Apartment Search/Apartment Scraper/dataFiles/apartmentClassPointer.json','/Volumes/GoogleDrive/My Drive/Projects/Apartment Search/Apartment Scraper/dataFiles/ignore.json')
    print(apt.link)

if __name__ == "__main__":
    main()

