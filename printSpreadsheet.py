import os
import json
import xlsxwriter
from datetime import datetime

def main():
    json_filepath = os.path.abspath('/Volumes/GoogleDrive/My Drive/Projects/Apartment Search/Apartment Scraper/dataFiles/apartmentsData.json')
    excel_filepath = os.path.abspath('/Users/brandonmcclenathan/Library/CloudStorage/OneDrive-NorthCarolinaStateUniversity/Documents/Projects/Apartment Search.xlsx')
    write_to_excel(json_filepath,excel_filepath)

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


if __name__ == "__main__":
    main()