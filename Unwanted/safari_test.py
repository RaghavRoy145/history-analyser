import os
import sqlite3
from shutil import copyfile
from pathlib import Path
from csv import writer
import pandas as pd

OUTDIR = "Output"
sql = """SELECT 
  datetime(visit_time + 978307200, 'unixepoch', 'localtime') as visit_time, url
FROM 
  history_visits
INNER JOIN 
  history_items ON
    history_items.id = history_visits.history_item
ORDER BY 
  visit_time DESC"""
firefox_path = os.path.join(Path.home(), "Library/Safari")
history_file = os.path.join(OUTDIR, "Copied_History_Safari")
copyfile(os.path.join(firefox_path, "History.db"), history_file)
conn = sqlite3.connect(history_file)
cursor = conn.cursor()
cursor.execute(sql)

file = os.path.join(OUTDIR, "safari.csv")
with open(file, "w", newline='') as csv_file:
        csv_writer = writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(cursor)

df = pd.read_csv(file)

print(df)