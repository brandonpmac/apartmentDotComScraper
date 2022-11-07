import argparse
import urllib.parse
import urllib.request
import requests
from bs4 import BeautifulSoup
import os
import parseHtml

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

    # If a link was specified
    if args.link != None:
        scrapeLink(args.link)

    # If update was specified
    if args.update == 'yes':
        updateSheet()

# ---------- Functions ----------
def scrapeLink(link):
    parsedLink = urllib.parse.urlparse(link)        # Parsing the link to get the network location
    if parsedLink.netloc != 'www.apartments.com':   # If the link is not located at apartments.com, raise an exception
        raise Exception('Error: Incompatible Link')

    # Defining the headers
    HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    }
    # Pulling data from apartments.com
    htmlText = requests.get(link,timeout=5,headers=HEADERS).text
    # Parsing the html text to get the info from site
    parseHtml.parseHtml(htmlText)
    

def updateSheet():
    pass

if __name__ == "__main__":
    main()