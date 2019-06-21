import argparse
import csv

import gspread
from oauth2client.service_account import ServiceAccountCredentials

parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--client-secrets",
    required=True,)

def main():

    opts = parser.parse_args()
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(opts.client_secrets, scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("BET account balance").sheet1

    # Extract and print all of the values
    list_of_hashes = sheet.get_all_records()
    print(list_of_hashes)

    with open('balance.csv', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            print(row)
            sheet.append_row(row)

    list_of_hashes = sheet.get_all_records()
    print(list_of_hashes)

if __name__ == "__main__":
    main()