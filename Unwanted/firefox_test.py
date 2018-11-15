import sqlite3
from datetime import datetime
import os
from shutil import copyfile
from pathlib import Path
from csv import writer
import pandas as pd

OUTDIR = "OUTPUT"

#sql = """select url, title, last_visit_date
#        from moz_historyvisits natural join moz_places where
#        last_visit_date is not null and url  like 'http%' and title is not null"""
sql = """select url, datetime(last_visit_date/1000000, 'unixepoch', 'localtime') as 'visit_time'
        from moz_historyvisits natural join moz_places where
        last_visit_date is not null and url  like 'http%' and title is not null"""
firefox_path = os.path.join(Path.home(), "Library/Application Support/Firefox/Profiles/")
history_file = os.path.join(OUTDIR, "Copied_HistoryF")
copyfile(os.path.join(firefox_path, [i for i in os.listdir(firefox_path) if i.endswith('.default')][0], "places.sqlite"), history_file)
conn = sqlite3.connect(history_file)
cursor = conn.cursor()
cursor.execute(sql)


file = os.path.join(OUTDIR, "firefox.csv")
with open(file, "w", newline='') as csv_file:
        csv_writer = writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(cursor)

df = pd.read_csv(file)

print(df)