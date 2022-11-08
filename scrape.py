import argparse
import urllib.parse
import urllib.request
import parseApartment
import os

def main():
    # ############### ARGUMENTS ###############
    # Defines all of the input 

    # Getting inputs from command line
    parser = argparse.ArgumentParser(description='Scrapes an apartment.com linkt to add data to a file.')

    # ---------- Command Line Arguments ----------
    # -l, --link:   Link command line argument
    parser.add_argument(
        '-l',   
        '--link',
        type=list,                   # Input type
        required=False,             # Making optional
        help='Adds link to apartmentLinks.txt and appends data to apartmentsData.json'
        )

    # -r, --remove: Remove command line argument
    parser.add_argument(
        '-r',
        '--remove',
        type=list,
        required=False,
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
    
    args = parser.parse_args()

    
    ulrFilePath = os.path.abspath('/Users/brandonmcclenathan/Library/Mobile Documents/com~apple~CloudDocs/Documents/Code/apartmentScraper - Shared Files/apartmentLinks.txt')
    
    # If a link was specified

    # Check to see if link is valid

    # Check to see if link has already been added

    # Add link to shared file

    if args.link != None:
        link = args.link
        parsedLink = urllib.parse.urlparse(link)       # Parsing the link to get the network location
        if parsedLink.netloc != 'www.apartments.com':       # If the link is not located at apartments.com, raise an exception
            raise Exception('Error: Incompatible Link')
        
        # Open the url txt file and read all the lines
        with open(ulrFilePath) as f:
            lines = f.readlines()

        if link in lines:
            print

        print(lines)

    # If update was specified
    if args.update == 'yes':
        updateSheet()
    
def scrapeLink(link):
    apartment = parseApartment.parseHtml(link)
    

def updateSheet():
    pass

if __name__ == "__main__":
    main()