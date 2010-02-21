#!/usr/bin/python
# coding: utf-8
"""
Author: Enrico Tröger
License: GPLv2
"""

from optparse import OptionParser
from database import VzUbcMonDatabase
from parser import VzUbcMonParser


UBC_FILE = '/proc/user_beancounters'
DATABASE_FILE = '/root/vzubcmon.pck'


###########################################################################
class VzUbcMon(object):
    """
    Check the current UBC values (in particular the failcnt) and compare it
    to the state of the last check. If the failcnt increased, report it
    to stdout.
    """

    #----------------------------------------------------------------------
    def __init__(self, ubc_filename, database_filename):
        self._parser = VzUbcMonParser(ubc_filename)
        self._database = VzUbcMonDatabase(database_filename)

    #----------------------------------------------------------------------
    def _print_report(self, changes):
        """
        Write a simple report to stdout

        | **param** changes (seq of str)
        """
        if changes:
            container_id = self._parser.get_information()[1]
            print 'Detected increased fail counts of UBC parameters for container ID %s' \
                % container_id
            for change in changes:
                print change

    #----------------------------------------------------------------------
    def check(self):
        """
        Compare the current UBC values against the ones from the last check
        """
        old_values = self._database.read()
        current_values = self._parser.get_resources()
        changed_values = []

        for resource_name in current_values:
            try:
                old_failcnt = old_values[resource_name].failcnt
            except KeyError:
                continue

            current_failcnt = current_values[resource_name].failcnt
            # check
            if current_failcnt > old_failcnt:
                msg = 'Increased failcnt for "%s" %s -> %s' % \
                    (resource_name, old_failcnt, current_failcnt)
                changed_values.append(msg)
            elif current_failcnt < old_failcnt:
                # if the current failcnt is less than the old one, the container
                # might be have been restarted, so reset the current value
                current_values[resource_name].failcnt = old_failcnt

        self._database.write(current_values)
        self._print_report(changed_values)


#----------------------------------------------------------------------
def main():
    """
    Main()
    """
    # arguments
    option_parser = OptionParser()
    option_parser.add_option('--database', dest='database', default=DATABASE_FILE,
        help=u'database file to store UBC failcounts [default: %s]' % DATABASE_FILE)
    option_parser.add_option('--ubc', dest='ubc_file', default=UBC_FILE,
        help=u'read user beancounters from this file [default: %s]' % UBC_FILE)
    arg_options = option_parser.parse_args()[0]

    # check
    vzubcmon = VzUbcMon(arg_options.ubc_file, arg_options.database)
    vzubcmon.check()


if __name__ == "__main__":
    main()
