from crontab import CronTab
from datetime import datetime, timedelta
import requests
import platform
import sys
import os
import gtfs_realtime_pb2
import multiprocessing
import threading
from concurrent.futures import ThreadPoolExecutor
from google.protobuf.json_format import MessageToJson
from urllib.parse import urlparse

# Constants needed for historical downloads
MINUTES = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
HISTORICAL_BASE_URL = "https://datamine-history.s3.amazonaws.com/gtfs"
HISTORICAL_URL_EXT = {
    "numbers" : "",
    "l": "l",
    "sir": "si"
}

# Constants needed for realtime downloading.
REALTIME_COLOR_TO_FEEDID = {
    "numbers" : "1",
    "blues"   : "26",
    "yellow"  : "16",
    "orange"  : "21",
    "l"       : "2",
    "sir"     : "11",
    "g"       : "31",
    "brown"   : "36",
    "purple"  : "51"
}

BASE_DIR = ""
STATS_FILENAME = ""
LINE = ""
DUMP_JSON = False
FEED_MESSAGE = gtfs_realtime_pb2.FeedMessage()

def now():
    return datetime.now().strftime("%Y%m%d-%H%M%S")

FILENAME_TS = now()

def log(line):
    print(line)
    with open(STATS_FILENAME, "a+") as f:
        f.write("[mta_download.py] {}: ".format(now()) + line)
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

def clear_all_crons():
    if platform.system() is 'Windows':
        print('ERR: can not clear cron jobs from windows system')
        return
    cron = CronTab(user=os.getenv('USER'))
    for job in cron
        if job.comment == 'mta_download':
            cron.remove(job)
            cron.write()

def handle_response(base_dir, response, filename, dump_json):
    if dump_json:
        filename = filename + ".json"
        try:
            with open(os.path.join(base_dir, "{}".format(filename)), "w+") as f:
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

def add_cron_job(nondated_url, curr_date):
    user = os.environ.get('USER', '')
    if user is '':
        usage("no USER env var set.")
    api_key = os.environ.get('MTA_API_KEY', '')
    if api_key is '':
        usage("no MTA_API_KEY env var set. Please run `export MTA_API_KEY=<KEY>` and try again.")
    if platform.system() is 'Windows':
        # daily at 23:50
        cron = CronTab(tab="""50 23 * * * pyenv activate mta && python {}/cron.py {} {} {} {} {} {}""".format(os.getcwd(), api_key, curr_date, DIRECTORY, REALTIME_COLOR_TO_FEEDID[LINE], LINE, STATS_FILENAME))
        cron.write()
    else:
        cron = CronTab(user="{}".format(user))
        job = cron.new(command="pyenv activate mta && python {}/cron.py {} {} {} {} {} {}".format(os.getcwd(), api_key, curr_date, DIRECTORY, REALTIME_COLOR_TO_FEEDID[LINE], LINE, STATS_FILENAME), comment="mta_downloader-{}".format(FILENAME_TS))
        job.setall('50 23 * * *')
        cron.write()

def download_range(nondated_url, date_begin, date_end):
    curr_date = date_begin;
    while (curr_date < date_end):
        if curr < datetime.now():
            download(nondated_url, curr_date)
        else:
            add_cron_job()
        curr_date += timedelta(days=1)

def download_historical_internal(dt, full_url):
    response = requests.get(full_url)
    if response.ok:
        log("Successfully downloaded {}".format(dt))
        handle_response(BASE_DIR, response, urlparse(full_url).path.replace('/',''), DUMP_JSON)
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
    return HISTORICAL_BASE_URL + HISTORICAL_URL_EXT[LINE]

def stats_filename():
    return os.path.join(BASE_DIR, "run-" + FILENAME_TS + ".txt")

def main():
    if len(sys.argv) != 5 and len(sys.argv) != 6:
        usage(len(sys.argv))
    global LINE
    LINE = sys.argv[1]
    # validate the line
    if LINE not in HISTORICAL_URL_EXT:
        if LINE not in REALTIME_COLOR_TO_FEEDID:
            usage("unrecognized line parameter: {}".format(line))
        else:
            log("selected line is not available for historical download.")
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
    if start_date.year < 2014:
        usage("Historical data is unavailable before 2014.")
    if not os.path.isdir(sys.argv[4]):
        usage("output directory = {} not found".format(sys.argv[4]))
    # did this param include the trailing slash? this normalizes both possibilities.
    global BASE_DIR
    global STATS_FILENAME
    BASE_DIR = os.path.join(sys.argv[4], "")
    global FILENAME_TS
    STATS_FILENAME = stats_filename()
    if len(sys.argv) == 6:
        if sys.argv[5] != "--json":
            usage("--json flag not passed in correctly")
        global DUMP_JSON
        DUMP_JSON = True
    log("Running mta_download.py. Command was: {}".format(" ".join(sys.argv)))
    url = build_nondate_url()
    download_range(url, start_date, end_date)
    print("Done. diagnostics at {}".format(stats_filename())))

if __name__ == "__main__":
    main()
