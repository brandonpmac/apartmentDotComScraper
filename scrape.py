import argparse
import urllib.parse
import urllib.request
import parseHtml
import os

def main():
    # ----- Getting inputs from command line -----
    parser = argparse.ArgumentParser(description='Scrapes an apartment.com linkt to add data to a file.')
    # Link command line argument
    parser.add_argument(
        '-l',
        '--link',
        type=str,
        required=False,
        metavar='LINK',
        help='Apartments.com link to parse.')

    # Update command line argument
    parser.add_argument(
        '-u',
        '--update',
        type=str,                   # Input type
        required=False,             # Setting to optional
        metavar='UPDATE',           # Alternate Name
        help='Update the currrent links in the file.',  # Description
        choices=['yes','no'],       # Defining the choices
        default='no'                # Setting the default value to 'no'
        )
    args = parser.parse_args()

    # ----- Defining the shared file paths -----
    ulrFilePath = os.path.abspath('/Users/brandonmcclenathan/Library/Mobile Documents/com~apple~CloudDocs/Documents/Code/apartmentScraper - Shared Files/apartmentLinks.txt')
    

    # If a link was specified
    if args.link != None:
        parsedLink = urllib.parse.urlparse(args.link)        # Parsing the link to get the network location
        if parsedLink.netloc != 'www.apartments.com':   # If the link is not located at apartments.com, raise an exception
            raise Exception('Error: Incompatible Link')
        
        with open(ulrFilePath) as f:
            pass

    # If update was specified
    if args.update == 'yes':
        updateSheet()
    
def scrapeLink(link):
    apartment = parseHtml.parseHtml(link)
    

def updateSheet():
    pass

if __name__ == "__main__":
    main()