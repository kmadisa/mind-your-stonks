# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Removed

### Changed

## [1.0.0] 2019-12-10

### Added

- Created a `BetClient` class encapsulating all the behaviour in the deleted `bet_stats.py` and `spreadsheet.py` modules [PR#15](https://github.com/kmadisa/mind-your-stonks/pull/15)..
- A utility classs that wraps the Selenium webdriver object [PR#15](https://github.com/kmadisa/mind-your-stonks/pull/15)..

### Removed

- Deleted the `bet_stats.py` and `spreadsheet.py` scripts [PR#15](https://github.com/kmadisa/mind-your-stonks/pull/15).
- Usage of the [python-gspread-sheets](https://github.com/CROSP/python-gspread-sheets) package.

### Changed

- Support for the new spreadsheet with nicely formatted tables for easy use.
- Moved around the spreadsheet columns:
    | Date | Timestamp | Balance | Money in bets | Loss/Gain | % Decrease/Increase |
    [PR#27](https://github.com/kmadisa/mind-your-stonks/pull/27).

## [0.0.1] - 2019-10-26

### Added

- This CHANGELOG file to hopefully serve as an evolving example of a
  standardized open source project CHANGELOG.
- README has instructions on how to use the project [PR#14](https://github.com/kmadisa/mind-your-stonks/pull/14).
- Added support to be able to navigate through pages [PR#12](https://github.com/kmadisa/mind-your-stonks/pull/1)2.
- Computing the amount of money that has been placed in bets [PR#9](https://github.com/kmadisa/mind-your-stonks/pull/9).
- Added scripts to scrape [BET.co.za](https://www.bet.co.za) site and writes the data
  to the Google sheet [PR#1](https://github.com/kmadisa/mind-your-stonks/pull/1).
