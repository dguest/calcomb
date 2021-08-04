#!/usr/bin/env python3

"""
Make a more reasonable ics file from an unreasonable one
"""

from argparse import ArgumentParser
from urllib.request import Request, urlopen
from sys import stdout
import re

def get_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('urls', nargs='+')
    parser.add_argument('-m','--matches', nargs='*', default=['HH-->4b'])
    return parser.parse_args()

key_regex = re.compile('(SUMMARY|URL|DESCRIPTION):.+')

class Event:
    keyed: dict
    event: list
    active: bool
    def __init__(self):
        self.keyed = {}
        self.event = []
        self.active = False


def event_iter(file_like):
    event = Event()
    for raw in file_like:
        line = raw.decode('utf-8').strip()
        if line == 'BEGIN:VEVENT':
            if event.active:
                raise Exception('found event in event')
            event.active = True
        if line == 'END:VEVENT':
            yield event.keyed, '\n'.join(event.event + [''])
            event = Event()
        if event.active:
            if key_regex.match(line):
                key, val = line.split(':',1)
                event.keyed[key] = val
            event.event += [line]

def run():
    args = get_args()
    for url in args.urls:
        req = Request(url)
        for edict, event in event_iter(urlopen(req)):
            if any(m in edict['SUMMARY'] for m in args.matches):
                stdout.write(event)

if __name__ == '__main__':
    run()
