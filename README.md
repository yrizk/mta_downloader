# mta_downloader: Batch Downloader for Historical NYC MTA Train data
Downloads the archived mta train data (starting from 2014) 
onto your machine.

## How to install 
Requirements 
    - pyenv/pyvirtualenv which manages different versions of python and also
      manages the dependencies 
    - `sudo pip3 install pipenv` and https://github.com/pyenv/pyenv-installer to install pipenv and pyenv respectively

1.  clone the repository and cd into it.
2.  `pyenv virtualenv 3.8.1 mta_downloader`
3.  `pyenv activate mta_downloader`
4.  `pipenv install` to install the dependencies.

## Usage: 
```
Usage: python mta_download.py LINE START_DATE END_DATE DIR [--json]
Please note: this script is sensitive to the order of the passed in
params. All arguments are required.
    LINE: Which train line to download from. One of numbers,l,sir for trains 1-6, the L train, and the staten island railway respectively.
    START_DATE: Form YYYY-MM-DD e.g 2020-01-01.
    END_DATE: Exclusive. Form YYYY-MM-DD e.g 2020-01-02.
    DIRECTORY: the directory for output, must already exist
    --json: convert the output from gtfs_pb2.FeedMessage binary protos to json
```

## A Note about the data source: 
unfortunately the data on the mta servers appears to be sparse
this is based on looking from 2017-09-17 ~ 2017-10.

Here the information is displayed in a table.
```
line | success | fail
1-6  | 8667    | 260
sir  | 0       | 1630 
l    | 0       | 8928
```
