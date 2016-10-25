#!/usr/bin/env python3.5

# Scrape ZPA weekly timetable and create an iCal feed.
#
# valentin@unimplemented.org, Tue Oct 25 10:05:49 CEST 2016
#
# Requirements: python3 (tested with 3.5),
#               BeautifulSoup4 (`pip install BeautifulSoup4`)
#               icalendar (`pip install icalendar`)
#               requests (`pip install requests`)

# TODO:
# - certificate pinning
# - convert date strings to objects
# - error handling
# - cache old weeks

from datetime import datetime, timedelta
import re, os, sys
import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event, vDatetime

zpa_base_url = "https://w3-o.cs.hm.edu:8000/"

# XXX stolen from stackoverflow
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

if __name__ == "__main__":
    # XXX use proper getopt
    if len(sys.argv) < 4:
        print("zpa2ics.py credentials.conf output.ics from-week to-week")
        print("Note: from-week and to-week are expected to be in the format")
        print("      DD.MM.YYYY!")
        sys.exit(1)

    cred_file = sys.argv[1]
    outfile = sys.argv[2]
    fromweek = datetime.strptime(sys.argv[3], "%d.%m.%Y")
    toweek = datetime.strptime(sys.argv[4], "%d.%m.%Y")

    username = None
    password = None
    with open(cred_file) as fh:
        line = fh.readline().rstrip()
        parts = line.split(":")
        username = parts[0]
        password = parts[1]

    # Create session and get csrftoken, can be reused for all future requests
    client = requests.session()
    client.verify = False
    client.get(zpa_base_url + "login/?")
    csrftoken = client.cookies['csrftoken']

    login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken, next='/')
    r = client.post(zpa_base_url + "login/", data=login_data, headers=dict(Referer="/"))

    # Slurp all weeks into RAM
    weeks = []
    now = fromweek
    while True:
        now += timedelta(weeks=1)
        weekplan_data = dict(csrfmiddlewaretoken=client.cookies['csrftoken'], date=now.strftime("%d.%m.%Y"))
        r = client.post(zpa_base_url + "student/week_plan/", data=weekplan_data, headers=dict(Referer="/student/week_plan/"))
        weeks.append(r.text)

        if now > toweek:
            break

    cal = Calendar()
    lectures = {}
    for week in weeks:
        soup = BeautifulSoup(week, 'html.parser')
        # This selects all "normal"/"level 1" timeslots this week
        for lect in soup.select("div .slot_1"):
            tslot = lect.attrs["id"]
            # We can assign any timeslot to a day by looking at the DOM parent
            day = datetime.strptime(lect.parent.attrs["id"], "%d.%m.%Y").date()
            start_end_time = soup.select("div #%s .slot_header" % tslot)[0].string.rstrip().lstrip().split(" - ")
            name = soup.select("div #%s .slot_inner" % tslot)[0].contents[0].lstrip()
            desc = soup.select("div #%s .slot_inner" % tslot)[0].contents[1]
            lecturer = False
            loc = False

            if desc:
                for line in desc:
                    # remove some whitespaces
                    line = " ".join(str(line).split())
                    # The description contains important information in the
                    # following format: Vorlesung IB IF1B / R1.006 / Blabla, P.
                    match = re.match(r"^([^\/]+) \/ ([^\/]+) \/ (.+)$", str(line))
                    if match:
                        loc = striphtml(match.group(2)).rstrip().lstrip()
                        lecturer = striphtml(match.group(3)).rstrip().lstrip()
                # wtf?
                desc = " ".join(striphtml(str(desc)).split())
            else:
                desc = "-"

            if "Tutorium" in desc:
                name += " Tutorium"
            if "Praktikum" in desc:
                name += " Praktikum"

            retry = False
            while True:
                try:
                    new_lecture = {
                        "name": name,
                        "desc": desc,
                        "lecturer": lecturer,
                        "loc": loc,
                        "start_time": datetime.strptime(start_end_time[0] + " " + lect.parent.attrs["id"], "%H:%M %d.%m.%Y"),
                        "end_time": datetime.strptime  (start_end_time[1] + " " + lect.parent.attrs["id"], "%H:%M %d.%m.%Y")
                    }
                    break
                except ValueError:
                    if retry:
                        print("skipping valueerror")
                        break
                    if "Fällt aus!" in start_end_time[1]:
                        start_end_time[1] = start_end_time[1].split("\n")[0].rstrip()
                    print(start_end_time)
                    retry = True
                    continue

            if not retry:
                if day in lectures:
                    lectures[day].append(new_lecture)
                else:
                    lectures[day] = [new_lecture]
            else:
                print("Skipping canceled lecture:")
                print(new_lecture)

    for d in sorted(lectures):
        #print(" == %s ==" % d.strftime("%d.%m.%Y"))
        for l in sorted(lectures[d], key=lambda h: h["start_time"]):
            event = Event()
            event['dtstart'] = vDatetime(l["start_time"]).to_ical()
            event.add('summary', l["name"])
            event.add('description', l["desc"])
            event.add('duration', l["end_time"] - l["start_time"])
            if "loc" in l:
                event.add('location', l["loc"])
            else:
                print("no loc")
            cal.add_component(event)
            #print("%s: %s (%s)" % (l["start_time"].strftime("%H:%M"), l["name"], l["desc"]))

    with open(outfile, 'w') as fh:
        fh.write(cal.to_ical().decode("utf-8"))
