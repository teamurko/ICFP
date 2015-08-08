#!/usr/bin/env python

import time
import json
from optparse import OptionParser
import .lib


def main():
    parser = OptionParser()
    parser.add_option(
        "-f", "--file", dest="filenames", action='append',
        help="File containing json encoded input"
    )
    parser.add_option(
        "-t", "--time", dest="time", type='int',
        help="Time limit, in seconds, to produce output"
    )
    parser.add_option(
        "-m", "--memory", dest="memory", type='int',
        help="Memory limit, in megabytes, to produce output"
    )
    parser.add_option(
        "-c", "--cores", dest="cores", type='int',
        help="Number of processor cores available"
    )
    parser.add_option(
        "-p", "--phrase", dest="phrases", action='append',
        help="Phrase of power"
    )
    (options, args) = parser.parse_args()
    start_time = time.time()
    expected_end_time = start_time + options.time
    result = []
    for input_file in options.filenames:
        input_json = json.loads(input_file) 
        # ignore phrases, cores, memory for now
        result.append(lib.solve(input_json, expected_end_time))
    print json.dumps(result)

if __name__ == '__main__':
    main()
