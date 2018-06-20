#!/c/Python36/python.exe
# !/usr/bin/env python3
"""Script application to save work time on a file.

Usage:
  worktime.py start now
  worktime.py start at <time>
  worktime.py end now
  worktime.py end at <time>
  worktime.py save
  worktime.py create
  worktime.py today
  worktime.py prediction | forecast
  worktime.py (-h | --help)
  worktime.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --report      Report all saved work times.

"""
import datetime
import os
import sqlite3
from datetime import timedelta as td
from pathlib import Path

from docopt import docopt
from peewee import *

db_path = None
with open('database.txt') as f:
    db_path = os.path.expanduser(f.readline())

conn = sqlite3.connect(db_path)

# db = SqliteDatabase('people.db')
#
#
# class TimeTracker(Model):
#     time = DateTimeField()
#
#     class Meta:
#         database = db
#
#
# class Person(Model):
#     name = CharField()
#     birthday = DateField()
#     is_relative = BooleanField()
#
#     class Meta:
#         database = db  # This model uses the "people.db" database.
#
#
# def create_db_person():
#     db.connect()
#     db.create_tables([Person, TimeTracker])
#     db.close()


def hours_today():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM time_register WHERE date(dtime) = date(?) ORDER BY dtime ASC",
                   (datetime.datetime.now(),))
    hours = cursor.fetchall()
    conn.close()
    return hours


def work_hours_today():
    hours = hours_today()
    hours = [x[0] for x in hours]
    total = td()
    for s, e in zip(hours[::2], hours[1::2]):
        st = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")
        et = datetime.datetime.strptime(e, "%Y-%m-%d %H:%M:%S.%f")
        ds = td(hours=st.hour, minutes=st.minute, seconds=st.second)
        de = td(hours=et.hour, minutes=et.minute, seconds=et.second)
        total += de - ds
    if len(hours) % 2 == 1:
        s = hours[-1]
        st = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")
        et = datetime.datetime.now()
        ds = td(hours=st.hour, minutes=st.minute, seconds=st.second)
        de = td(hours=et.hour, minutes=et.minute, seconds=et.second)
        total += de - ds
    return total


def main():
    arguments = docopt(__doc__, version='Work Time 0.1')
    if arguments["create"]:
        create_db_person()
    if arguments["save"]:
        c = conn.cursor()
        dt_now = datetime.datetime.now()
        c.execute("INSERT INTO time_register VALUES (?)", (dt_now,))
        conn.commit()
        print("time saved [{}]".format(dt_now))
        conn.close()
    if arguments["today"]:
        print("How many hours did you work today?\n Exactly {}".format(work_hours_today()))
    if arguments["forecast"] or arguments["prediction"]:
        message = "If you work continuously from now, what time will you finish your journey?"
        remaining = (td(hours=9) - work_hours_today()) + datetime.datetime.now()
        print(message + "\n Exactly {}".format(remaining))


# TODO: Persist on database the number of hours a day necessary to finish the journey, that way the forecast is based
#  on that. Add parameters to create it, and edit it.


if __name__ == '__main__':
    main()
