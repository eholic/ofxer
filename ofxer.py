#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 MXXIV.net
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php

"""
CSV to OFX converter.
A script of converting CSV files exporting from your credit and bank account
"""

import csv
import os
import itertools as it
import pandas as pd
from csv2ofx import utils
from csv2ofx.ofx import OFX
from io import StringIO
from meza.io import read_csv, IterStringIO
from operator import itemgetter

import argparse
import textwrap


class Ofxer:
    """ OFX Converter """
    def __init__(self, csvfile, option):
        """
        load csvfile using option

        :param string csvfile: path of csvfile
        :param dict option: loading options
        """
        if not os.path.exists(csvfile):
            raise FileNotFoundError

        # options you must have
        for k in ['skiprows', 'usecols']:
            if k not in option:
                raise AttributeError("option['{}'] missing.".format(k))
        # options you might have
        for k in ['parser', 'encoding']:
            if k not in option:
                option[k] = None

        # switch loading mode
        col_num = len(option['usecols'])
        if col_num == 3:
            self.is_bank = False
        elif col_num == 4:
            self.is_bank = True
        else:
            raise AttributeError("length of option['usecols'] must be 3 or 4")

        self._df = self.__load_csv(csvfile, option)

    def __load_csv(self, csvfile, option):

        if self.is_bank:
            colnames = ('date', 'title', 'withdraw', 'deposit')
        else:
            colnames = ('date', 'title', 'amount')

        df = pd.read_csv(csvfile, index_col=0,
                         skiprows=option['skiprows'],
                         usecols=option['usecols'],
                         encoding=option['encoding'],
                         names=colnames)

        # courtesy for Japanese
        if option['parser'] is None:
            df.index = df.index.str.replace(r'[年月日]', '/')

        # parse datetime and remove invalid rows
        def __try_todate(text):
            try:
                pd.to_datetime(text, format=option['parser'])
                return True
            except Exception:
                return False
        df = df[df.index.map(lambda x: __try_todate(x))]
        df.index = pd.to_datetime(df.index, format=option['parser'])

        # make missing value to zero
        if self.is_bank:
            df['withdraw'].fillna(0, inplace=True)
            df['deposit'].fillna(0, inplace=True)
        df = df[~df.isnull().any(axis=1)]

        # trim special characters
        def __to_num(df):
            if df.dtype == 'object':
                not_num_or_dot = r'([^\d\.])'
                df = df.str.replace(not_num_or_dot, '').fillna(0)
                df = df.astype(float)
            return df

        if self.is_bank:
            df['deposit'] = __to_num(df['deposit'])
            df['withdraw'] = __to_num(df['withdraw'])
            df['amount'] = df['deposit'].add(-df['withdraw'], fill_value=0)
        else:
            df['amount'] = -(__to_num(df['amount']))

        return df

    def write_ofx(self, ofxfile):
        """ write out ofxfile from DataFrame """
        mapping = {
            'account': 'account',
            'date': itemgetter('date'),
            'payee': itemgetter('title'),
            'amount': itemgetter('amount'),
            }

        ofx = OFX(mapping)
        data = self._df.to_csv(quoting=csv.QUOTE_ALL)
        records = read_csv(StringIO(data))
        groups = ofx.gen_groups(records)
        cleaned_trxns = ofx.clean_trxns(groups)
        data = utils.gen_data(cleaned_trxns)

        content = it.chain([ofx.header(), ofx.gen_body(data), ofx.footer()])

        with open(ofxfile, 'wb') as f:
            for line in IterStringIO(content):
                f.write(line)


def col_act():
    # Note: https://stackoverflow.com/questions/4194948/python-argparse-is-there-a-way-to-specify-a-range-in-nargs
    class ColumnAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            nmin = 3
            nmax = 4
            if not nmin <= len(values) <= nmax:
                msg = 'argument "{f}" requires between {nmin} and {nmax} arguments'.format(
                    f=self.dest, nmin=nmin, nmax=nmax)
                raise argparse.ArgumentTypeError(msg)
            # check dupulication
            if len(values) != len(set(values)):
                msg = 'argument "{f} {v}" dupulicated'.format(
                    f=self.dest, v=values)
                raise argparse.ArgumentTypeError(msg)

            setattr(args, self.dest, values)
    return ColumnAction


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog='ofxer.py',
                description='CSV to OFX converter.\nA script of converting CSV files exporting from your credit and bank account',
                formatter_class=argparse.RawTextHelpFormatter,
                epilog='-------------------------------------------------------------------------------',
                add_help=True,
                )

    parser.add_argument('csvfile',          action='store',   nargs=None,                          help='csv file exported from your credit or bank acount')
    parser.add_argument('-p', '--parser',   action='store',   nargs=None, default=None,            help="specify the date format if special e.g. '%%Y年%%m月%%d日'")
    parser.add_argument('-o', '--output',   action='store',   nargs=None, default='output.ofx',    help='path to write ofx file (default: output.ofx)')
    parser.add_argument('-s', '--skiprows', action='store',   nargs=None, required=True, type=int, help='skipping number of csv file headers (incl. column name)')
    parser.add_argument('-e', '--encoding', action='store',   nargs=None, default=None,            help='file encoding')
    parser.add_argument('-c', '--usecols',  action=col_act(), nargs='+',  required=True, type=int, help=textwrap.dedent('''\
                                                                                                        column index number of
                                                                                                          date title amount
                                                                                                          (e.g. --usecols 0 4 5)
                                                                                                          or
                                                                                                          date title withdraw deposit
                                                                                                          (e.g. --usecols 0 3 10 5)
                                                                                                          Note: counting from ZERO
                                                                                                        '''))

    args = parser.parse_args()

    options = {'parser': args.parser,
               'skiprows': args.skiprows,
               'usecols': args.usecols,
               'encoding': args.encoding}
    print(options)

    ofxer = Ofxer(args.csvfile, options)
    ofxer.write_ofx(args.output)

    print('Successfully converted to {}'.format(args.output))
