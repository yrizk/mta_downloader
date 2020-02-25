from datetime import datetime
from datetime import timedelta
import requests
import sys
import os

"""
Top Level TODOs
v0: just works
    - 1 line
    - optional end_date
    - the key can be a env var

v1: this is the version that we will release
    - variable number of lines.
    - better error handling
        - more graceful parsing
    - logging
    - dumps a file to describe the current run
"""
MINUTES = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
BASE_URL = "https://datamine-history.s3.amazonaws.com/gtfs"
URL_EXT = {
    "numbers" : "",
    "l": "l",
    "sir": "si"
}

BASE_DIR = ""
STATS_FILENAME = ""
LINE = ""

def log(line):
    print(line)
    with open(STATS_FILENAME, "a+") as f:
        f.write(line)
        f.write("\n")

def usage(extra_str=""):
    # TODO what if the directory already exists? did we make it on a previous run?
    # let's punt this for later.
    print("""
            {}

            Usage: python mta_download.py LINE START_DATE END_DATE DIR
            Please note: this script is sensitive to the order of the passed in
            params. All arguments are required.
                LINE: Which train line to download from. One of {numbers,l,SIR} for trains 1-6, the L train, and the staten island railway respectively.
                START_DATE: Form YYYY-MM-DD e.g 2020-01-01.
                END_DATE: Exclusive. Form YYYY-MM-DD e.g 2020-01-02.
                DIRECTORY: the directory for output, must already exist
          """.format(extra_str))
    sys.exit(-1)

def parse(date_str):
    return datetime.strptime(date_str,'%Y-%m-%d').date()

def handle_response(response, dt):
    with open(os.path.join(BASE_DIR, "{}".format(dt)), "wb+") as f:
        f.write(response.content)

def download_range(nondated_url, date_begin, date_end):
    curr_date = date_begin;
    while (curr_date < date_end):
        download(nondated_url, curr_date)
        curr_date += timedelta(days=1)

def download(nondated_url, curr_date):
    for hr in range(24):
        for m in MINUTES:
            dt = "%s-%02d-%02d" % (str(curr_date), hr, m)
            full_url = nondated_url + "-%s" % (dt)
            response = requests.get(full_url)
            if response.status_code < 400:
                log("Successfully downloaded {}".format(dt))
                handle_response(response, dt)
            else:
                log("Error on {}. Status Code = {}".format(dt, response.status_code))

def build_nondate_url():
    return BASE_URL + URL_EXT[LINE]

def main():
    if len(sys.argv) != 5:
        usage()
    global LINE
    LINE = sys.argv[1]
    # validate the line
    if LINE not in URL_EXT:
        usage("unrecognized line parameter: {}".format(line))
    start_date = sys.argv[2]
    end_date = sys.argv[3]
    # validate the dates
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
    if not os.path.isdir(sys.argv[4]):
        usage("output directory = {} not found".format(sys.argv[4]))
    # did this param include the trailing slash? this normalizes both possibilities.
    global BASE_DIR
    global STATS_FILENAME
    BASE_DIR = os.path.join(sys.argv[4], "")
    STATS_FILENAME = os.path.join(BASE_DIR, "run-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt")
    log("Running mta_download.py with start date = {} and end date = {}".format(start_date, end_date))
    url = build_nondate_url()
    download_range(url, start_date, end_date)

if __name__ == "__main__":
    main()
