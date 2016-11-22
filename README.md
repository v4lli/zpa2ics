# zpa2ical scraper

Scrapes the new [HM FK07](http://www.cs.hm.edu/) ZPA system and converts
the personalized weekly time table to an iCalendar feed file.  iCal
feeds are compatible with almost all calendar systems (including Gmail)
as well as most calendar apps.

![Calendar view example](/ical.png)

## Requirements

* python3 (tested with 3.5)
* BeautifulSoup4 (`pip install BeautifulSoup4`)
* icalendar (`pip install icalendar`)
* requests (`pip install requests`)

# Usage
Put your login credentials into a text file, separated by a colon
(htaccess-style). Pass the path to this file as the first parameter to
zpa2ics.py.

Example credential file:

<pre>ifw1234:foobar</pre>

Example call which scrapes all weeks from WS16/17:

<pre>$ ./zpa2ics.py ~/.zpa_login.conf /var/www/stundenplan.ics 04.10.2016 01.02.2017</pre>

It's probably a good idea to add zpa2ics.py to crontab and re-fetch it e.g. daily:

<pre>@daily chronic /home/valentin/zpa2/zpa2ics.py ...</pre>

## Note
This is a quick-and-dirty implementation. The code might look rather adventurous.

The code currently does not verify the (invalid) ZPA certificate. Only use
on trusted networks!

Alternative lectures ("yellow boxes") are currently NOT handled
correctly (although this should be easily fixable).

## TODO
- handle alternative lectures ("Ausweichtermin bzw. Raumänderung")
- certificate pinning
- convert date strings to objects
- error handling
- all weeks but the current one
- don't re-fetch past weeks
- log out when finished?
