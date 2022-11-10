import requests
import json
from bs4 import BeautifulSoup

class apartment():

    def __init__(self,link,classPointerFilepath) -> None:
        
        # Defining the apartment link
        self.link = link

        # Getting apartmentClassPointers
        with open(classPointerFilepath,'r') as f:
            self.pointers = json.load(f)
        
        # Getting the data to parse through from website
        self.data = self.scrapeLink(self.link)

        # Defining the address
        self.Address =  self.findData('Address')
        self.City =     self.findData('City')
        self.State =    self.findData('State')
        self.Zip =      self.findData('Zip')

        # Getting rid of the data cause I don't want it stored in the class
        del self.data
        del self.pointers

    def scrapeLink(self,link):
        """Inputs"""
         # Defining the headers for the html request
        HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        }
        # Pulling data from apartments.com
        htmlText = requests.get(link,timeout=5,headers=HEADERS).text    # Getting the html data from apartments.com
        return htmlText.split('\n')

    def findData(self,key):
        # Defining the flag
        flag = self.pointers[key]
        # create a list of the row of each occurance of the specified pointer in the data
        position = [i for i,row in enumerate(self.data) if flag[0] in row]
        
        if len(position) == 1:
            return clean(self.data[position[0]+flag[1]])

def clean(rawString):
        """Cleans the data from bad formating"""
        soup = BeautifulSoup(rawString, 'html.parser')
        return soup.find_all()[0].text

def main():
    apt = apartment('https://www.apartments.com/the-franklin-at-crossroads-raleigh-nc/h1gzdt2/','/Users/brandonmcclenathan/Library/Mobile Documents/com~apple~CloudDocs/Documents/Code/apartmentScraper - Shared Files/dataFiles/apartmentClassPointer.json')
    print(apt.link)

if __name__ == "__main__":
    main()

