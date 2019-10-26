[![Build Status](https://travis-ci.org/kmadisa/mind-your-stonks.svg?branch=master)](https://travis-ci.org/kmadisa/mind-your-stonks)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# Mind your *stonks*


![Screen_Shot_2019-06-05_at_1 26 32_PM](https://user-images.githubusercontent.com/16665803/61865197-15e25e00-aed3-11e9-8541-4fff382916b7.jpg)

## The Story
[BET.co.za](https://bet.co.za) does not have an easier way to track the changes in the user's account balance. All that it displays is the current account balance. In order to get an idea of **how much you had vs how much you have** in your account, you have to sift through lots and lots of pages on the transaction history, not to mention the brutal experience the user will have to go through to compute the **account's balance at a particular moment in time** from all that information.

The purpose of this project is to provide [BET.co.za](https://bet.co.za) clients an easier way to keep track of the changes occurring in their account balance.

Basically there is utility script that run and log into the client's [BET.co.za](https://bet.co.za) account (using [Selenium](https://selenium-python.readthedocs.io/)) and read the value of the current balance and uploads the data to a [Google Sheets](https://docs.google.com/spreadsheets/u/0/), where then it can be visualized.


&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **AND JUST LIKE THAT YOU KNOW THE RISE & FALL OF YOUR STONKS !!!!**


## Get Started

1. Obtain Google API for authentication:
    *   Follow the instructions [here](https://gspread.readthedocs.io/en/latest/oauth2.html#oauth-credentials)

2. Install ensure that `geckodrive` for Firefox is installed.
    *   Download [geckodriver](https://github.com/mozilla/geckodriver)
        *   ```wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz```
        *   Extract: ```tar -xvzf geckodriver-v0.24.0-linux64.tar.gz```
    *   `sudo cp geckodriver /usr/local/bin`

3. Install Selenium:
    *   `pip install selenium`

4. Install the python-gspread-sheets package:
    *   `pip install -r requirements.txt`

5. Upload a copy of the [spreadsheet](https://docs.google.com/spreadsheets/d/1k--fJt5qC191RMHH3D2MbhRhaIJb__WTEBjOL1rcksc/edit?usp=sharing) to your own GDrive or [GSpeadsheet](https://docs.google.com/spreadsheets).

![Screenshot from 2019-10-26 15-57-25](https://user-images.githubusercontent.com/16665803/67620667-959d0300-f809-11e9-9048-eed3f950521e.png)
Figure 1. A snapshot of the spreadsheet columns.

#### Table columns
   * *Date*: date reading was made (yyyy-mm-dd).
   * *Timestamp*: indicated when the script logged into the account hh:mm PM/AM.
   * *Balance*: the current balance in the account in S.A rands.
   * *Money in bets*: the amount of money placed in a bet which is still unresolved.
   * *Actual Loss/Gain*: difference between the previous known balance and the current one
                         (+ money in bets).
   * *% Increase*: calculated from the previous known balance and the current one (+ money in bets).

## Usage

```bash
python bet_stats.py -h
usage: query_balance.py [-h] [--update-spreadsheet UPDATE_SPREADSHEET]
                        username password

Scrape the BET.co.za website to obtain the account balance. It also writes the
data to a Google Spreadsheet.

positional arguments:
  username              Bet.co.za registered email address
  password              Bet.co.za account password.

optional arguments:
  -h, --help            show this help message and exit
  --update-spreadsheet UPDATE_SPREADSHEET
                        Update spreadsheet with new data. This requires the
                        client_secret.json file for authentication. It is
                        downloaded from the Google Developers' Console.
```

Typical usage:
```bash
query_balance.py $USERNAME $PASSWORD --update-spreadsheet ./client_secret.jsons
```

## Travis CI automated daily balance reader
Travis CI can automatically run your Google App Engine based application, by encrypting your `clients_secrets.json` file and pushing it to `GitHub`.
See: https://docs.travis-ci.com/user/deployment/google-app-engine/


## Feedback

Feel free to fork it or send me PR to improve it.
