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


class SpreadsheetColumn(Constant):
    (DATE, TIMESTAMP, MONEY_IN_BETS, BALANCE,
     GAIN_LOSS, PERCENTAGE_INCREASE) = map(chr, range(65, 71))


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

    table_entry = {}
    table_entry["Date"] = "=DATE({},{},{})".format(
        *(str(datetime.date(datetime.now())).split("-")))
    table_entry["Timestamp"]= better.timestamp
    
    better.goto_betting_history()
    better.filter_betting_history(BetStatus.UNSETTLED)
    
    table_entry["Money_in_bets"] = better.compute_money_invested()
    table_entry["Balance"]= better.current_balance

    better.sign_out()

    if opts.update_spreadsheet:

        gsheet_manager = GoogleSheetManager(credentials_path=opts.update_spreadsheet[1],
                                            sheet_id="1DWRxtnTIHiRuQ9w1Yq4TiZJqidIZhguiGadYDNgnZsI")
        gsheet_manager.start_session()

        previous_row_num = len(gsheet_manager.get_all_rows())
        current_row_num = previous_row_num + 1
        table_entry["Gain_loss"] = "=MINUS(SUM({0}{2},{1}{2}),{0}{3})".format(
            SpreadsheetColumn.BALANCE, SpreadsheetColumn.MONEY_IN_BETS, current_row_num,
            previous_row_num
        )
        table_entry["Percentage_increase"] = "=ROUND(MINUS({0}{1},{0}{2})/{0}{2}, 2)".format(
            SpreadsheetColumn.BALANCE, current_row_num, previous_row_num)

        # Write to the spreadsheet
        # Spreadsheet columns
        # | Date | Timestamp | Money in bets | Balance | Loss/Gain | % Increase |
        gsheet_manager.append_row(list(table_entry.values()))

        gsheet_manager.close_session()

if __name__ == "__main__":
    main()
