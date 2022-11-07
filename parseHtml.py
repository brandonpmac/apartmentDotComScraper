import os
from bs4 import BeautifulSoup

def main():
    with open(os.path.abspath('./403Data.html'),'r') as f:
        rawData = f.read()
    parseHtml(rawData)

 
def parseHtml(rawData):
    data = rawData.split('\n')
    

if __name__ == "__main__":
    data = main()


