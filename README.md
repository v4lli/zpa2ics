# zpa2ical scraper

Scrapes the new HM ZPA system and converts the weekly plan to an
iCalendar file.

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

## Note
The code currently does not verify the (invalid) ZPA certificate. Only use
on trusted networks.
