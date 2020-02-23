from datetime import datetime
import sys

"""
Top Level TODOs
v0: just works
    - 1 line
    - no times.

v1:
    - variable number of lines.
    - better error handling
        - more graceful parsing
    - logging
"""

#TODO expand verbage to talk about what each of the params mean (form of the dates)
def usage():
    print("""
            Usage: python mta_download.py LINE START_DATE [END_DATE] [DIRECTORY]
            Please note: this script is sensitive to the order of the passed in
            params.
                LINE: the specific line to download data for.()
                START_DATE: Form YYYY-MM-DD e.g 2020-01-01. Required
                END_DATE: Exclusive. Form YYYY-MM-DD e.g 2020-01-02. Optional (default is today)
                DIRECTORY: the directory for output. Optional (default =
                $HOME/mta_download)
          """)
    sys.exit(-1)

#TODO include the ability to pass in time as well
def parse(date_str):
    pass

#TODO
def download_range(date_begin, date_end):
    pass

def download():
    pass

def main():
    #TODO validate each of the flags (is there a package I can import for this?)
    # right now, start_date and end_date are required, and output dir is
    # predetermined
    if len(sys.argv) != 3:
        usage()
    start_date = sys.argv[1]
    end_date = sys.argv[2]
    print("Running mta_download.py with start date = {} and end date = {}".format(start_date, end_date))
    start_date = parse(start_date)
    end_date = parse(end_date)
    download_range(start_date, end_date)

if __name__ == "__main__":
    main()
