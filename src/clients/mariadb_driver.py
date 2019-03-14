"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0.  If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Copyright 2019- Stichting Sqalpel

Author: M. Kersten

Execute a single query multiple times on the database nicknamed 'dbms'
and return a list of timings. The first error encountered stops the sequence.
The result is a dictionary with at least the structure {'times': [...]}
"""

import re
import subprocess
import shlex
import time
import tempfile
import configparser
import datetime
import os

class MariaDBDriver:

    def __init__(self):
        pass

    @staticmethod
    def run(target, query):
        """
        The number of repetitions is used to derive the best-of value.
        :param target:
        :return:
        """
        db = target['db']
        query = target['query']
        params = target['params']
        socket = target['dbsocket']
        runlength = int(target['runlength'])
        timeout = int(target['timeout'])
        debug = target.getboolean('debug')
        response = {'error': '', 'times': [], 'cnt': [], 'clock': [], 'extra':[]}
        try:
            preload = [ "%.3f" % v for v in list(os.getloadavg())]
        except os.error:
            preload = 0
            pass

        conn = None
        try:
            conn = mysql.connector.connect(port=target['port'], database=db, user='root')
        except (Exception, mysql.connector.DatabaseError) as msg:
            print('Connection', target['port'], db)
            print('Exception', msg)
            if conn:
                conn.close()
                print('Database connection closed')
            return response

        if debug:
            nu = time.strftime('%Y-%m-%d %H:%m:%S', time.localtime())
            print('Run query:', nu, ':',  query)

        for i in range(runlength):
            try:
                nu = time.strftime('%Y-%m-%d %H:%m:%S', time.localtime())
                c= conn.cursor()
                ms = datetime.datetime.now()
                c.execute(query)
                response['answer'] = 'No answer'
                ms = datetime.datetime.now() - ms
            except mysql.connector.DatabaseError as msg:
                # a timeout should also stop the database process involved the hard way
                print('EXCEPTION ', i,  msg)
                response['error'] = str(msg).replace("\n", " ").replace("'", "''")
                conn.close()
                return response

            if debug:
                print('response ', proc.stdout.decode('ascii')[:-1])

            response['times'].append(float(ms.microseconds) / 1000.0)
            response['cnt'].append(-1)  # not yet collected
            response['extra'].append([])
            response['clock'].append(nu)
        try:
            postload = [ "%.3f" % v for v in list(os.getloadavg())]
        except os.error:
            postload = 0
            pass
        response['cpuload'] = str(preload + postload).replace("'", "")
        conn.close()
        return response