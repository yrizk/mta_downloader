from datetime import datetime, timedelta
import requests
import sys
import os
import gtfs_realtime_pb2
import multiprocessing
import threading
from concurrent.futures import ThreadPoolExecutor
from google.protobuf.json_format import MessageToJson
from urllib.parse import urlparse

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
DUMP_JSON = False
FEED_MESSAGE = gtfs_realtime_pb2.FeedMessage()

def now():
    return datetime.now().strftime("%Y%m%d-%H%M%S")

FILENAME = now()

def log(line):
    print(line)
    with open(STATS_FILENAME, "a+") as f:
        f.write("{}: ".format(now()) + line)
        f.write("\n")

def usage(extra_str="Incorrect Usage"):
    print("""
            {}

            Usage: python mta_download.py LINE START_DATE END_DATE DIR [--json]
            Please note: this script is sensitive to the order of the passed in
            params. All arguments are required.
                LINE: Which train line to download from. One of numbers,l,sir for trains 1-6, the L train, and the staten island railway respectively.
                START_DATE: Form YYYY-MM-DD e.g 2020-01-01.
                END_DATE: Exclusive. Form YYYY-MM-DD e.g 2020-01-02.
                DIRECTORY: the directory for output, must already exist
                --json: convert the output from gtfs_pb2.FeedMessage binary protos to json
          """.format(extra_str))
    sys.exit(-1)

def parse(date_str):
    return datetime.strptime(date_str,'%Y-%m-%d').date()

def handle_response(response, filename):
    if DUMP_JSON:
        filename = filename + ".json"
        try:
            with open(os.path.join(BASE_DIR, "{}".format(filename)), "w+") as f:
                FEED_MESSAGE.Clear()
                FEED_MESSAGE.MergeFromString(response.content)
                f.write(MessageToJson(FEED_MESSAGE))
        except google.protobuf.message.DecodeError:
            log("Error parsing the binary into a FeedMessage for {}. Saving as raw binary instead".format(filename))
            with open(os.path.join(BASE_DIR, "{}".format(filename)), "wb+") as f:
                f.write(response.content)
    else:
        with open(os.path.join(BASE_DIR, "{}".format(filename)), "wb+") as f:
            f.write(response.content)

def download_range(nondated_url, date_begin, date_end):
    curr_date = date_begin;
    while (curr_date < date_end):
        download(nondated_url, curr_date)
        curr_date += timedelta(days=1)

def download_historical_internal(dt, full_url):
    response = requests.get(full_url)
    if response.ok:
        log("Successfully downloaded {}".format(dt))
        handle_response(response, urlparse(full_url).path.replace('/',''))
    else:
        log("Error on {}. Status Code = {}".format(dt, response.status_code))

def download(nondated_url, curr_date):
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = []
        for hr in range(24):
            for m in MINUTES:
                dt = "%s-%02d-%02d" % (str(curr_date), hr, m)
                full_url = nondated_url + "-%s" % (dt)
                futures.append(executor.submit(download_historical_internal, dt, full_url))
        for f in futures:
            f.result()

def build_nondate_url():
    return BASE_URL + URL_EXT[LINE]

def main():
    if len(sys.argv) != 5 and len(sys.argv) != 6:
        usage(len(sys.argv))
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
    global FILENAME
    STATS_FILENAME = os.path.join(BASE_DIR, "run-" + FILENAME + ".txt")
    if len(sys.argv) == 6:
        if sys.argv[5] != "--json":
            usage("--json flag not passed in correctly")
        global DUMP_JSON
        DUMP_JSON = True
    log("Running mta_download.py. Command was: {}".format(" ".join(sys.argv)))
    url = build_nondate_url()
    download_range(url, start_date, end_date)
    print("Done. diagnostics at {}".format(os.path.join(BASE_DIR, "run-" + FILENAME + ".txt")))

if __name__ == "__main__":
    main()
