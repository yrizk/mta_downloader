import requests
import os
import sys
import mta_download

REALTIME_BASE_URL="http://datamine.mta.info/mta_esi.php?key=%s&feed_id=%s"
API_KEY = ""
FEED_ID = ""
DT = ""
LINE = ""
STATS_FILENAME = ""
BASE_DIR = ""

def log(line):
    with open(STATS_FILENAME, 'a') as f:
        f.write("[cron.py] {}: ".format(mta_download.now()) + line)
        f.write("\n")

def handle_response(reponse):

def download(dt, full_url, api_key, feed_id, line):
    response = requests.get(full_url % (api_key, feed_id))
    if response.ok:
        mta_download.handle_response(BASE_DIR, response, "{}-{}".format(dt,line))
    else:
        log("Error on {} for realtime request. Status Code = {}".format(dt, response.status_code))

if __name__ == "__main__":
    # start parsing arguments
    global API_KEY, FEED_ID, DT, LINE, STATS_FILENAME
    if len(sys.argv) != 6:
        log("Incorrect number of arguments")
        sys.exit(-1)
    API_KEY = sys.argv[1]
    DT = sys.argv[2]
    BASE_DIR = sys.argv[3]
    FEED_ID = sys.argv[4]
    LINE = sys.argv[5]
    download(DT, REALTIME_BASE_URL, API_KEY, FEED_ID, LINE)
