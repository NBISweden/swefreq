#!/usr/bin/env python3
'''
Baseclass for the data importers
'''

import os
import sys
import gzip
import time
import logging
import urllib.request

import MySQLdb

class DataImporter():
    '''
    Baseclass for the data importers
    '''
    BLOCKSIZE = 1024

    def __init__(self, settings):
        self.settings = settings
        self.download_dir = settings.data_dir
        self.chrom = settings.limit_chrom
        self.batch_size = settings.batch_size
        self.progress_bar = not settings.disable_progress
        self.in_file = None

    def _connect(self, host, user, passwd, database):
        try:
            logging.info("Connecting to database {}".format(database))
            database = MySQLdb.connect(host=host,
                                       user=user,
                                       passwd=passwd,
                                       db=database)
            return database.cursor()
        except MySQLdb.Error as error:
            logging.error("Error connecting: {}".format(error))

    def _download(self, base_url, version=None):
        """
        Download a file into the download_dir.
        """
        url = base_url.format(version=version)
        filename = os.path.join(self.download_dir, url.split("/")[-1])
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        try:
            os.stat(filename)
            logging.info("Found file: {}, not downloading".format(filename))
            return filename
        except FileNotFoundError:
            pass

        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request)
        filesize = None
        if 'Content-length' in response.headers.keys():
            filesize = int(response.headers['Content-length'])
        else:
            logging.info("response lacks content-length header, but will still download.")
        downloaded = 0
        logging.info("Downloading file {}".format(url))
        with open(filename, 'wb') as out:
            last_progress = -1.0
            if filesize and self.progress_bar:
                last_progress = self._update_progress_bar(downloaded, filesize, last_progress)

            block = response.read(DataImporter.BLOCKSIZE)

            while block:
                downloaded += len(block)
                if self.progress_bar and logging.getLogger().getEffectiveLevel() < 30 and filesize:
                    last_progress = self._update_progress_bar(downloaded, filesize, last_progress)
                out.write(block)
                block = response.read(DataImporter.BLOCKSIZE)
        response.close()
        if self.progress_bar and logging.getLogger().getEffectiveLevel() < 30 and filesize:
            last_progress = self._update_progress_bar(downloaded, filesize,
                                                      last_progress, finished=True)
        return filename

    def _download_and_open(self, base_url, version=None):
        """
        Downloads a file and returns an open file handle
        """
        filename = self._download(base_url, version)
        return self._open(filename)

    def _open(self, filename, binary=True):
        mode = 'rb' if binary else 'rt'
        encoding = None if binary else 'utf8'
        try:
            logging.debug("Opening file {}".format(filename))
            return gzip.open(filename, mode, encoding=encoding) if filename.endswith(".gz") else open(filename)
        except IOError as error:
            logging.error("IOERROR: {}".format(error))

    def _time_format(self, seconds):
        hour, rem = divmod(seconds, 3600)
        mins, secs = divmod(rem, 60)
        retval = ""
        if hour:
            retval += "{:d} hours, ".format(int(hour))
        if mins:
            retval += "{:d} mins, ".format(int(mins))
        retval += "{:3.1f} secs".format(secs)
        return retval

    def _time_since(self, start):
        return self._time_format(time.time() - start)

    def _time_to(self, start, progress=0.01):
        return self._time_format((time.time() - start)/progress)

    def _update_progress_bar(self, current_count, total, last_progress, finished=False):
        if not finished:
            progress = current_count/total
        else:
            progress = 1.001
        if last_progress < 0:
            if logging.getLogger().getEffectiveLevel() < 30:
                sys.stderr.write("".join(["{:<10}".format(i) for i in range(0, 101, 10)]) + "\n")
                sys.stderr.write("| ------- "*10 + "|\n")
            last_progress = 0
        while progress > last_progress + 0.01:
            last_progress += 0.01
            sys.stderr.write("=")
            sys.stderr.flush()
        if finished:
            sys.stderr.write("\n")
        return last_progress
