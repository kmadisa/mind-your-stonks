# Mind your stonks


![Screen_Shot_2019-06-05_at_1 26 32_PM](https://user-images.githubusercontent.com/16665803/61865197-15e25e00-aed3-11e9-8541-4fff382916b7.jpg)

## The Story
[BET.co.za](https://bet.co.za) does not have an easier way to track the changes in the user's account balance. All that it displays is the current account balance. In order to get an idea of **how much you had vs how much you have** in your account, you have to sift through lots and lots of pages on the transaction history, not to mention the brutal experience the user will have to go through to compute the **account's balance at a particular moment in time** from all that information.

The purpose of this project is to provide [BET.co.za](https://bet.co.za) clients an easier way to keep track of the changes occurring in their account balance.

Basically there are utility scripts that run and log into the client's [BET.co.za](https://bet.co.za) account (using [Selenium](https://selenium-python.readthedocs.io/)) and read the value of the current balance and uploads the data to a [Google Sheets](https://docs.google.com/spreadsheets/u/0/), where then it can be visualized.


&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **AND JUST LIKE THAT YOU KNOW THE RISE & FALL OF YOUR STONKS !!!!**


## Installation

1. Obtain Google API for authentication:
    *   Follow the instructions [here](https://gspread.readthedocs.io/en/latest/oauth2.html#oauth-credentials)

2. Before you install ensure that `geckodrive` for Firefox is installed.
    *   Download [geckodriver](https://github.com/mozilla/geckodriver)
        *   ```wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz```
        *   Extract: ```tar -xvzf geckodriver-v0.24.0-linux64.tar.gz```
    *   `sudo cp geckodriver /usr/local/bin`

3. Now install:
    *   `pip install . -U`

4. Upload the [spreadsheet](docs/Shopping_List.xlsx) to GDrive or [GSpeadsheet](https://docs.google.com/spreadsheets), and insert your items into column 2 [ **Items** ]

## Usage

```bash
price_checker.py -h
usage: price_checker.py [-h] --json CLIENT_SECRET_FILE --spreadsheet_name
                        SPREADSHEET_NAME [--share-with SHARED] [--update]
                        [--loglevel LOG_LEVEL]

optional arguments:
  -h, --help            show this help message and exit
  --json CLIENT_SECRET_FILE
                        Google Json file containing secrets.
  --spreadsheet_name SPREADSHEET_NAME, -s SPREADSHEET_NAME
                        Name of the spreadsheet you want to open.
  --share-with SHARED   [email address] Share the spreadsheet with someone via
                        email
  --update              Update spreadsheet with new prices.
  --loglevel LOG_LEVEL  log level to use, default [INFO], options [INFO,
                        DEBUG, ERROR]
```

Typical usage:


## Oh, Thanks!

By the way... Click if you'd like to [say thanks](https://saythanks.io/to/mmphego)... :) else *Star* it.

✨🍰✨


## Travis CI automated daily price updates
Travis CI can automatically run your Google App Engine based application, by encrypting your `clients_secrets.json` file and pushing it to `GitHub`.
See: https://docs.travis-ci.com/user/deployment/google-app-engine/

## Feedback

Feel free to fork it or send me PR to improve it.
