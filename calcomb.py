#!/usr/bin/env python3

"""
Make a more reasonable ics file from an unreasonable one
"""
_raw_help = "Don't clean zoom links"
_advertisement='Indexed by calcomb: https://github.com/dguest/calcomb'
_def_veto = ['Cancelled','Postponed']

from argparse import ArgumentParser
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote
from sys import stdout
import re, os, time, hmac, hashlib
from textwrap import wrap
from collections import OrderedDict

def get_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('urls', nargs='+')
    parser.add_argument('-m','--matches', nargs='*', default=[''])
    parser.add_argument('-r','--raw', action='store_true', help=_raw_help)
    parser.add_argument('-k','--use-secret-key', action='store_true')
    parser.add_argument('-v','--veto', nargs='*', default=_def_veto,
                        help='default: %(default)s')
    return parser.parse_args()

key_regex = re.compile('^([-A-Z;=])+:.+')
password_regex = re.compile('([&?]pwd=)[A-Za-z0-9]+')

class Event:
    keyed: dict
    active: bool
    def __init__(self):
        self.keyed = OrderedDict()
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

def event_iter(file_like):
    event = Event()
    for raw in file_like:
        line = raw.decode('utf-8').rstrip('\r\n')
        if line == 'BEGIN:VEVENT':
            if event.active:
                raise Exception('found event in event')
            event.active = True
        if event.active:
            if key_regex.match(line):
                key, val = line.split(':',1)
                event.keyed[key] = val
                event.last_key = key
            elif line.startswith(' '):
                event.keyed[event.last_key] += line[1:]
            else:
                raise Exception(f"what is '{line}'?")
        if line == 'END:VEVENT':
            yield event.keyed
            event = Event()

def append_signature(url, key_file='~/.indico-secret-key'):
    lines = open(os.path.expanduser(key_file),'rb').read()
    api_key, secret_key = lines.split()
    items = sorted([
        ('timestamp', str(int(time.time()))),
        ('ak', api_key),
        ('from', '-30d00h00m'),
    ])
    encoded = urlencode(items)
    url_root, *rest = url.rsplit('/',3)
    url_rest = '/'.join(rest)
    to_hash = f'/{url_rest}?{encoded}'
    items.append(('signature',hmac.new(
        secret_key, to_hash.encode('utf8'), hashlib.sha1).hexdigest()))
    return f'{url_root}/{url_rest}?' + urlencode(items)

def run():
    args = get_args()

    def matcher(edict):
        if not any(m in edict['SUMMARY'] for m in args.matches):
            return False
        if any(v in edict['SUMMARY'] for v in args.veto):
            return False
        return True

    stdout.write(
        'BEGIN:VCALENDAR\r\n'
        'VERSION:2.0\r\n'
        'PRODID:-//CERN//INDICO//EN\r\n'
    )
    for url in args.urls:
        if args.use_secret_key:
            if not url.startswith('https:'):
                url = f'https://indico.cern.ch/export/categ/{url}.ics'
            url = append_signature(url)
        req = Request(url)
        for edict in event_iter(urlopen(req)):
            if matcher(edict):
                edict['DESCRIPTION'] += r'\n' + _advertisement
                listified = [f'{x}:{y}' for x, y in edict.items()]
                event = wrap_lines(listified, clean=(not args.raw))
                stdout.write(event)
    stdout.write(
        'END:VCALENDAR\r\n'
    )

if __name__ == '__main__':
    run()
