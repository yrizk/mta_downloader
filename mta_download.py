from datetime import datetime
from datetime import timedelta
import requests
import sys

"""
Top Level TODOs
v0: just works
    - 1 line
    - no times.
    - optional end_date
    - the key can be a env var

v1: this is the version that we will release
    - variable number of lines.
    - better error handling
        - more graceful parsing
    - logging
    - TODO: use argparse
    - dumps a file to describe the current ru
        - in it, we describe the datetimes that we expected to work
        but just didn't.
"""
MINUTES = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]

def usage(extra_str=""):
    # TODO what if the directory already exists? did we make it on a previous run?
    # let's punt this for later.
    print("""
            {}

            Usage: python mta_download.py LINE START_DATE [END_DATE] [DIRECTORY]
            Please note: this script is sensitive to the order of the passed in
            params.
                LINE: the specific line to download data for.()
                START_DATE: Form YYYY-MM-DD e.g 2020-01-01. Required
                END_DATE: Exclusive. Form YYYY-MM-DD e.g 2020-01-02. Optional (default is today)
                DIRECTORY: the directory for output. Optional (default =
                $HOME/mta_download)
          """.format(extra_str))
    sys.exit(-1)

def parse(date_str):
    return datetime.strptime(date_str,'%Y-%m-%d').date()

def handle_response(response):
    pass


def download_range(date_begin, date_end):
    curr_date = date_begin;
    while (curr_date < date_end):
        download(curr_date)
        curr_date += timedelta(days=1)

def download(curr_date):
    for hr in range(24):
        for m in MINUTES:
            url = "https://datamine-history.s3.amazonaws.com/gtfs-%s-%02d-%02d" % (str(curr_date), hr, m)
            print("downloading: {}".format(url))
            response = requests.get(url)
            if response.status_code < 400:
                handle_data(response)
            else:
                print("Error on date {} {}:{}. Status Code = {}".format(curr_date, hr, m, response.status_code))


def main():
    #TODO validate each of the flags (is there a package I can import for this?)
    # right now, start_date and end_date are required, and output dir is
    # predetermined
    if len(sys.argv) != 3:
        usage()
    #TODO consider factoring this stuff into its fn.
    start_date = sys.argv[1]
    end_date = sys.argv[2]
    if start_date == end_date:
        usage("Start Date is equal to the End Date. This does nothing.")
    try:
        start_date = parse(start_date)
    except ValueError:
        usage("Invalid START_DATE")
    try:
        end_date = parse(end_date)
    except ValueError:
        usage("Invalid END_DATE")
    print("Running mta_download.py with start date = {} and end date = {}".format(start_date, end_date))
    download_range(start_date, end_date)

if __name__ == "__main__":
    main()
