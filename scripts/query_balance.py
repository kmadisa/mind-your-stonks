#!/usr/bin/env python3
import argparse
from datetime import datetime
from aenum import Constant
from loguru import logger

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from mind_your_stonks.bet_client import BetClient, BetStatus


class SpreadsheetColumnLetter(Constant):
    (DATE, TIMESTAMP, BALANCE, MONEY_IN_BETS,
     GAIN_LOSS, PERCENTAGE_INCREASE) = map(chr, range(65, 71))


class SpreadsheetColumnNumber(Constant):
    (DATE, TIMESTAMP, BALANCE, MONEY_IN_BETS,
     GAIN_LOSS, PERCENTAGE_INCREASE) = range(1, 7)


OPENING_BALANCE_ROW = 4
CLOSING_BALANCE_ROW = 5


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
         " file for authentication. It is downloaded from the Google Developers'"
         " Console.",)


def is_leap_year(year):
    # Python program to check if year is a leap year or not
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


def main():

    opts = parser.parse_args()

    better = BetClient(opts.username, opts.password)
    better.sign_in()

    table_entry = {}
    table_entry["Date"] = "=DATE({},{},{})".format(
        *(str(datetime.date(datetime.now())).split("-")))
    table_entry["Timestamp"] = better.timestamp

    better.goto_betting_history()
    better.filter_betting_history(BetStatus.UNSETTLED)

    table_entry["Balance"] = better.current_balance
    table_entry["Money_in_bets"] = better.compute_money_invested()

    better.sign_out()

    if opts.update_spreadsheet:

        date_today = datetime.date(datetime.now())
        day = date_today.day
        month = date_today.strftime("%B")  # Get the month as text
        year = date_today.year
        months_with_30_days = ["April", "June", "September", "November"]
        leap_year_month = "February"

        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        # Use creds to create a client to interact with the Google Drive API
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            opts.update_spreadsheet, scope)
        client = gspread.authorize(creds)
        # Find a workbook by name and open the sheet of interest.
        # Make sure you use the right name here.
        logger.debug("Opening the Google spreadsheet...")
        spreadsheet = client.open("BET account balance")
        logger.debug("Started session on the Google sheet.")
        sheet = spreadsheet.worksheet("{} {}".format(month, year))

        # Update the opening/closing balance
        current_account_balance = table_entry["Balance"]
        if day == 1:
            sheet.update_cell(
                OPENING_BALANCE_ROW, SpreadsheetColumnNumber.BALANCE,
                current_account_balance)
            logger.debug("First day of the {} month!!! Setting the opening balance."
                         .format(month))
        elif day == 28 and month == leap_year_month and not is_leap_year(year):
            sheet.update_cell(
                CLOSING_BALANCE_ROW, SpreadsheetColumnNumber.BALANCE,
                current_account_balance)
            logger.debug("Last day of the {} month!!! Setting the closing balance."
                         .format(month))
        elif day == 29 and month == leap_year_month:
            sheet.update_cell(
                CLOSING_BALANCE_ROW, SpreadsheetColumnNumber.BALANCE,
                current_account_balance)
            logger.debug("Last day of the {} month!!! Setting the closing balance."
                         .format(month))
        elif day == 30 and month in months_with_30_days:
            sheet.update_cell(
                CLOSING_BALANCE_ROW, SpreadsheetColumnNumber.BALANCE,
                current_account_balance)
            logger.debug("Last day of the {} month!!! Setting the closing balance."
                         .format(month))
        elif day == 31:
            sheet.update_cell(
                CLOSING_BALANCE_ROW, SpreadsheetColumnNumber.BALANCE,
                current_account_balance)
            logger.debug("Last day of the {} month!!! Setting the closing balance."
                         .format(month))

        previous_row_num = len(sheet.get_all_values())
        current_row_num = previous_row_num + 1

        if day == 1:
            table_entry["Gain_loss"] = 0.00
            table_entry["Percentage_increase"] = 0.00
        else:
            table_entry["Gain_loss"] = (
                "=MINUS(SUM({0}{2},{1}{2}), SUM({0}{3},{1}{3}))".format(
                    SpreadsheetColumnLetter.BALANCE,
                    SpreadsheetColumnLetter.MONEY_IN_BETS,
                    current_row_num,
                    previous_row_num)
            )

            table_entry["Percentage_increase"] = (
                "={2}{3}/SUM({0}{4}, {1}{4})".format(
                    SpreadsheetColumnLetter.BALANCE,
                    SpreadsheetColumnLetter.MONEY_IN_BETS,
                    SpreadsheetColumnLetter.GAIN_LOSS,
                    current_row_num,
                    previous_row_num)
            )
        # Write to the spreadsheet
        # Spreadsheet columns
        # | Date | Timestamp | Balance | Money in bets | Actual Loss/Gain | % Decrease/Increase |
        logger.debug("COMMENCING: Writing data to the Google sheet.")
        sheet.append_row(list(table_entry.values()), value_input_option='USER_ENTERED')
        logger.debug("COMPLETE: Writing data to the Google sheet.")


if __name__ == "__main__":
    main()
