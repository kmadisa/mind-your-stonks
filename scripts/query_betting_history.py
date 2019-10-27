#!/usr/bin/env python3
import csv
import argparse
from datetime import datetime

from aenum import Constant
from loguru import logger

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from googlesheets.google_sheet_manager import GoogleSheetManager

from mind_your_stonks.bet_client import BetClient, BetStatus



parser = argparse.ArgumentParser(description="Scrape the BET.co.za website"
                                 " to obtain the account balance. It also"
                                 " writes the data to a Google Spreadsheet.")
parser.add_argument(
    "username",
    help="Bet.co.za registered email address",)
parser.add_argument(
    "password",
    help="Bet.co.za account password.",)
parser.add_argument(
    "--update-spreadsheet",
    help="Update spreadsheet with new data. This requires the client_secret.json"
        " file for authentication. It is downloaded from the Google Developers' Console.",)

def main():

    opts = parser.parse_args()

    better = BetClient(opts.username, opts.password)
    better.sign_in()
    
    better.goto_betting_history()
    bets = better.export_betting_history_data()

    better.sign_out()

    with open('betting_history_archive.csv', mode='w') as archive:
            archive_writer = csv.writer(archive, delimiter=" ", quotechar='"', quoting=csv.QUOTE_ALL)
            for bet in bets:
                archive_writer.writerow(bet)

    if opts.update_spreadsheet:

        gsheet_manager = GoogleSheetManager(credentials_path=opts.update_spreadsheet,
                                            sheet_id="1DWRxtnTIHiRuQ9w1Yq4TiZJqidIZhguiGadYDNgnZsI")
        gsheet_manager.start_session()

        previous_row_num = len(gsheet_manager.get_all_rows())
        current_row_num = previous_row_num + 1

        # Write to the spreadsheet
        # Spreadsheet columns
        # | Date | Timestamp | Money in bets | Balance | Loss/Gain | % Increase |

        gsheet_manager.close_session()

if __name__ == "__main__":
    main()
