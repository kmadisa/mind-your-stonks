#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from mind_your_stonks.bet_client import BetClient

bc = BetClient("k", "*")
options = Options()
options.headless = True

drv = webdriver.Firefox(options=options)
drv.get('file:///home/kmadisa47/Desktop/ticket3.html')
bc.driver = drv

bet_data = bc._extract_ticket_data()

for metadata, fields, table in zip(bet_data[0], bet_data[1], bet_data[2]):
    print(metadata)
    print(fields)
    print("###########################")
    for t in table:
        print(t)
    print("###########################")
