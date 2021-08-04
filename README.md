Calendar Combiner
=================

Indico makes pretty reasonable `.ics` files if you know how to find
them and if conveners can be bothered to keep events relatively
categorized. Unfortunately most conveners have more important
convening to do, so the indico index in any given group is usually a
nightmare of events that no one cares about. That in turn means that
subscribing to the group `.ics` fill is just adding noise to your
calendar.

This is a script to help.

How to use
----------

You can run it like

```
calcomb.py <url to events.ics file> [more urls...] -m <match 1> [match...]
```

Where it's very important that you include the URL with your
`user_token=*` at the end.

You can combine as many URLs as you like, and then run as a cron job
that dumps everything to another public URL. Then you can unsubscribe
from those reminder emails and get some real work done.
