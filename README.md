Calendar Combiner
=================

Indico makes pretty reasonable `.ics` files if you know how to find
them and if conveners can be bothered to keep events relatively
categorized. Unfortunately most conveners have more important
convening to do, so the indico index in any given category is usually
a nightmare of events that no one cares about. That in turn means that
subscribing to the category `events.ics` file is just adding noise to
your calendar.

This is a script to help.

How to use
----------

You can run it like

```
calcomb.py <url to events.ics file> [more urls...] -m <match 1> [match...]
```

Where it's very important that you include the URL with your
`user_token=*` at the end. **Hint:** you can get the full url with the
token by clicking the little calendar dohikcy on the upper right side
of the indico category. The `match` field just matches the event
summary, i.e. something like `comb` will match "SUSY + exotics global
combination meeting", "thedotcombubble" etc.

You can combine as many URLs as you like, and then run as a cron job
that dumps everything to another public URL. Then you can unsubscribe
from those reminder emails and get some real work done.

### Private Key Mode ###

You can also use [Indico's export API][export-api] to avoid creating a
special token for each event and embedding that token in the call. The
syntax is

```
calcomb.py <catigory id> [more ids] -k -m <match 1> [match...]
```

Note that you'll need a local file called `~/.indico-secret-key` which
should contain [your indico credentials][cred]. It have the format

```
XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
YYYYYYYY-YYYY-YYYY-YYYY-YYYYYYYYYYYY
```

where first line is the token, second is the "secret".


[export-api]: https://indico.readthedocs.io/en/v1.9/http_api/
[cred]: https://indico.cern.ch/user/api/
