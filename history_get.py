prof = input("Enter profile number (0 for default): ")

import sqlite3
import pandas
import csv
import datetime
import matplotlib.pyplot as plt
from shutil import copyfile
from pathlib import Path
import sys
import os

if not os.path.exists("Output"): os.mkdir("Output")
def OutputDirectory():
    if sys.platform=="win32":
        return "Output\\"
    elif sys.platform=="linux" or sys.platform=="darwin":
        return "Output/"
def copyHistory(prof="Default"):
    if sys.platform=="win32":
        copyfile(str(Path.home())+"\\AppData\\Local\\Google\\Chrome\\User Data\\" + prof + "\\History", OutputDirectory()+"Copied_History")
    elif sys.platform=="linux" or sys.platform=="darwin":
        copyfile(str(Path.home())+"/Library/Application Support/Google/Chrome/" + prof + "/History", OutputDirectory()+"Copied_History")


if prof != "0":
    copyHistory("Profile "+prof)

else:
    copyHistory()

conn = sqlite3.connect(OutputDirectory()+"Copied_History")
cursor = conn.cursor()
cursor.execute("SELECT datetime(visits.visit_time/1000000-11644473600, 'unixepoch', 'localtime') as 'visit_time',urls.url from urls,visits WHERE urls.id = visits.url ORDER BY visit_time DESC")

file = OutputDirectory()+"url_visittime.csv"

with open(file, "w", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(cursor)

dataset = pandas.read_csv(file)
#dataset["visit_time"] = dataset["visit_time"].apply(lambda x: str(x[:7])) #To get only year and month in date
#print(dataset.groupby("visit_time").size()) #Number of sites visited in each month
dataset["visit_time"] = dataset["visit_time"].apply(lambda x: str(x[11:13]))
dataset = dataset.sort_values(ascending=False, by="visit_time")
times_frequency = dataset.groupby("visit_time").size()
times_only = []
frequency_of_times = []
print(times_frequency)
for i in times_frequency.keys():
    times_only.append(int(i))
    frequency_of_times.append(int(times_frequency[i]))

dataset["url"] = dataset["url"].str.split("/").str[2]    #split url by / and get only the website name
dataset["url"] = dataset["url"].str.replace("www.","")
url_frequency = dataset.groupby("url").size() #Number of times each website is visited
url_frequency = url_frequency.sort_values(ascending=False)
url_frequency.to_csv(OutputDirectory() + "url_frequency.csv")
url_frequency = url_frequency[url_frequency > 10]

urls = []
frequency = []
for i in url_frequency.keys():
    urls.append(i)
    freq = url_frequency[i]
    frequency.append(freq)


print("Top 50 most used:")
for j in url_frequency.keys()[:50]:
    print(j," - ",url_frequency[j])

def time_24hours_to_12hours(time_24):
    time_12 = ""
    if 0 < time_24 < 12:
        time_12 = str(time_24) + " AM"
    elif time_24 == 0:
        time_12 = "12 AM"
    elif time_24 == 12:
        time_12 = "12 PM"
    elif 12 < time_24 < 24:
        time_12 = str(time_24 - 12) + " PM"
    return time_12
times_only_12hours = list(map(time_24hours_to_12hours, times_only))

"""plt.figure(figsize=(8,8))
#pie_chart = fig.add_subplot(211)
plt.axis('equal')
plt.pie(frequency, labels=urls[:10]+["" for x in range(0,len(urls)-10)], labeldistance=1.05, rotatelabels=True)
plt.savefig(OutputDirectory()+"pie_chart.svg")
#plt.show()
#bar_graph = fig.add_subplot(212)
x_ticks = range(len(urls))
plt.figure(figsize=(16,9))
plt.bar(x_ticks, frequency)
plt.xticks(range(len(urls)), urls, rotation="vertical")
plt.tight_layout()
#plt.show()
plt.savefig(OutputDirectory()+"bar_graph.svg")
plt.close()"""

"""fig, axes = plt.subplots(2,2,figsize=(14,9))
#pie_chart = fig.add_subplot(311)
axes[0,0].axis("equal")
axes[0,0].pie(frequency, rowspan=2, labels=urls[:10]+["" for x in range(0,len(urls)-10)], labeldistance=1.05, rotatelabels=True)

#bar_graph = fig.add_subplot(312)
x_ticks = range(len(urls))
axes[0,1].bar(x_ticks, frequency)
plt.sca(axes[1])
plt.xticks(range(len(urls)), urls, rotation="vertical")

#times = fig.add_subplot(313)
axes[1,1].bar(times_only, frequency_of_times)

fig.tight_layout()

plt.show()"""

fig = plt.figure(figsize=(16,9))
gs = fig.add_gridspec(ncols = 4, nrows = 2)
pie_ax = fig.add_subplot(gs[0:2,0:2])
bar1_ax = fig.add_subplot(gs[0,2:4])
bar2_ax = fig.add_subplot(gs[1,2:4])

pie_ax.axis("equal")
pie_ax.pie(frequency, labels=urls[:10]+["" for x in range(0,len(urls)-10)], labeldistance=1, rotatelabels=True)

x_ticks = range(len(urls))
bar1_ax.bar(x_ticks, frequency)
plt.sca(bar1_ax)
plt.xticks(range(len(urls)), urls, rotation="vertical", fontsize=5)

bar2_ax.bar(times_only, frequency_of_times)
plt.sca(bar2_ax)
plt.xticks(times_only, times_only_12hours, rotation="vertical")

plt.tight_layout()
plt.savefig(OutputDirectory()+"Graphs.pdf", format="pdf")
plt.show()
plt.close()
