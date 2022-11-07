import argparse

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

    
    

if __name__ == "__main__":
    main()