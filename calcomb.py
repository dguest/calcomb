#!/usr/bin/env python3

"""
Make a more reasonable ics file from an unreasonable one
"""
_raw_help = "Don't clean zoom links"

from argparse import ArgumentParser
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote
from sys import stdout
import re, os, time, hmac, hashlib
from textwrap import wrap

def get_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('urls', nargs='+')
    parser.add_argument('-m','--matches', nargs='*', default=['HH-->4b'])
    parser.add_argument('-r','--raw', action='store_true', help=_raw_help)
    parser.add_argument('-k','--use-secret-key', action='store_true')
    return parser.parse_args()

key_regex = re.compile('(SUMMARY|URL|DESCRIPTION):.+')
password_regex = re.compile('([&?]pwd=)[A-Za-z0-9]+')

class Event:
    keyed: dict
    event: list
    active: bool
    def __init__(self):
        self.keyed = {}
        self.event = []
        self.active = False
        self.last_key = None

def wrap_lines(lines, clean):
    wrapped = []
    for line in lines:
        if clean:
            line = password_regex.sub(r' [ZOOM PASSWORD REDACTED] ', line)
        wrapped += wrap(
            line,
            width=75,
            subsequent_indent=" ",
            drop_whitespace=False,
            replace_whitespace=False,
        )
    return '\r\n'.join(wrapped + [''])

def event_iter(file_like, clean=True):
    event = Event()
    for raw in file_like:
        line = raw.decode('utf-8').rstrip('\r\n')
        if line == 'BEGIN:VEVENT':
            if event.active:
                raise Exception('found event in event')
            event.active = True
        if event.active:
            if line.startswith(' '):
                event.event[-1] += line[1:]
                event.keyed[event.last_key] += line[1:]
            else:
                event.event += [line]
            if key_regex.match(line):
                key, val = line.split(':',1)
                event.keyed[key] = val
                event.last_key = key
        if line == 'END:VEVENT':
            yield event.keyed, wrap_lines(event.event, clean=clean)
            event = Event()

def append_signature(url, key_file='~/.indico-secret-key'):
    lines = open(os.path.expanduser(key_file),'rb').read()
    api_key, secret_key = lines.split()
    items = {'timestamp': str(int(time.time()))}
    encoded = urlencode(items)
    url = f'{url}?{encoded}'.encode('utf8')
    print(url, secret_key)
    items['signature'] = hmac.new(secret_key, url, hashlib.sha1).hexdigest()
    encoded = urlencode(items)
    return f'{url}?{encoded}'

def run():
    args = get_args()
    stdout.write(
        'BEGIN:VCALENDAR\r\n'
        'VERSION:2.0\r\n'
        'PRODID:-//CERN//INDICO//EN\r\n'
    )
    for url in args.urls:
        if args.use_secret_key:
            url = append_signature(url)
        req = Request(url)
        for edict, event in event_iter(urlopen(req), clean=(not args.raw)):
            if any(m in edict['SUMMARY'] for m in args.matches):
                stdout.write(event)
    stdout.write(
        'END:VCALENDAR\r\n'
    )

if __name__ == '__main__':
    run()
