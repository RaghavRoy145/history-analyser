prof = input("Enter profile number (0 for default): ")

from time import perf_counter as time
start_total = time()
start = time()
from sqlite3 import connect
from pandas import read_csv
from csv import writer
import matplotlib.pyplot as plt
from shutil import copyfile
from pathlib import Path
from sys import platform
from os import path, mkdir
from calendar import month_name
print("Time to import:", round(time()-start, 2), "s")

start = time()
if not path.exists("Output"): mkdir("Output")
outdir = "Output"

history_path = ""
if platform=="win32":
    history_path = path.join(Path.home(), "AppData\\Local\\Google\\Chrome\\User Data", prof, "History")
elif platform=="linux":
    history_path = path.join(Path.home(), ".config/google-chrome", prof, "History")
elif platform=="darwin":
    

def copyHistory(prof="Default"):
    pt = ""
    if platform=="win32":
        pt = path.join(Path.home(), "AppData\\Local\\Google\\Chrome\\User Data", prof, "History")
    elif platform=="linux":
        pt = path.join(Path.home(), ".config/google-chrome", prof, "History")
    elif platform=="darwin":
        pt = path.join(Path.home(), "Library/Application Support/Google/Chrome/", prof, "History")
    copyfile(pt, path.join(outdir, "Copied_History"))
if prof != "0" and prof != "":
    copyHistory("Profile "+prof)
else:
    copyHistory()
print("Time to copy history:", round(time()-start, 2), "s")

start = time()
conn = connect(path.join(outdir, "Copied_History"))
cursor = conn.cursor()
cursor.execute("SELECT datetime(visits.visit_time/1000000-11644473600, 'unixepoch', 'localtime') as 'visit_time',urls.url from urls,visits WHERE urls.id = visits.url ORDER BY visit_time DESC")

file = path.join(outdir, "url_visittime.csv")

with open(file, "w", newline='') as csv_file:
        csv_writer = writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(cursor)
print("Time to save history as csv:", round(time()-start, 2), "s")

start = time()
dataset = read_csv(file)
#dataset["visit_time"] = dataset["visit_time"].apply(lambda x: str(x[:7])) #To get only year and month in date
#print(dataset.groupby("visit_time").size()) #Number of sites visited in each month
dataset_copy = dataset.copy()
dataset["visit_time"] = dataset["visit_time"].apply(lambda x: str(x[11:13]))
dataset = dataset.sort_values(ascending=False, by="visit_time")
times_frequency = dataset.groupby("visit_time").size()
times_only = list(times_frequency.keys())
frequency_of_times = list(times_frequency.values)

dataset["url"] = dataset["url"].str.split("/").str[2]    #split url by / and get only the website name
dataset["url"] = dataset["url"].str.replace("www.","")
url_frequency = dataset.groupby("url").size() #Number of times each website is visited
url_frequency = url_frequency.sort_values(ascending=False)
url_frequency.to_csv(path.join(outdir, "url_frequency.csv"))
url_frequency = url_frequency[url_frequency > 10]

urls = (list(url_frequency.keys()))
frequency = (list(url_frequency.values))

print("Top 50 most used:")
for j in url_frequency.keys()[:50]:
    print(j," - ",url_frequency[j])

def time_24hours_to_12hours(time_24):
    time_12 = ""
    time_24 = int(time_24)
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


dataset_copy["visit_time"] = dataset_copy["visit_time"].apply(lambda x: str(x[:7])) #To get only year and month in date
groupedby_months = dataset_copy.groupby("visit_time").size()
month_years = list(groupedby_months.keys())
number_of_sites_visited_in_months = list(groupedby_months.values)

print("Time to analyse:", round(time()-start, 2), "s")


start = time()

fig = plt.figure(figsize=(16,9))
gs = fig.add_gridspec(ncols = 3, nrows = 2)
pie_ax = fig.add_subplot(gs[0,0])
bar3_ax = fig.add_subplot(gs[1,0])
bar1_ax = fig.add_subplot(gs[0,1:3])
bar2_ax = fig.add_subplot(gs[1,1:3])

pie_ax.axis("equal")
pie_ax.pie(frequency, labels=urls[:15]+["" for x in range(0,len(urls)-15)], labeldistance=1, rotatelabels=True)

x_ticks = range(len(urls))
bar1_ax.bar(x_ticks, frequency)
bar1_ax.set_xlabel("Website url")
plt.sca(bar1_ax)
plt.xticks(x_ticks, [], rotation="vertical", fontsize=5)
rects = bar1_ax.patches
for rect, label in zip(rects, urls):
    bar1_ax.text(rect.get_x() + rect.get_width() / 2, 5, label,
            ha='center', va='bottom', fontsize=4, rotation="vertical")

bar2_ax.bar(times_only, frequency_of_times)
plt.sca(bar2_ax)
plt.xticks(times_only, [], rotation="vertical")
rects = bar2_ax.patches
for rect, label in zip(rects, times_only_12hours):
    height = rect.get_height()
    bar2_ax.text(rect.get_x() + rect.get_width() / 2, height + 5, label,
            ha='center', va='bottom', fontsize="x-small")
bar2_ax.set_xlabel("Time")

x_ticks = range(len(groupedby_months))
bar3_ax.bar(x_ticks, number_of_sites_visited_in_months)
bar3_ax.set_xlabel("Month and Year")
plt.sca(bar3_ax)
plt.xticks(x_ticks, [], rotation="vertical")
rects = bar3_ax.patches
months = [x[:4]+"\n"+month_name[int(x[5:])] for x in month_years]
for rect, label in zip(rects, months):
    height = rect.get_height()
    bar3_ax.text(rect.get_x() + rect.get_width() / 2, height/2 - height/10, label,
            ha='center', va='bottom', fontsize="small")


plt.tight_layout()
plt.savefig(path.join(outdir, "Graphs.pdf"), format="pdf")

print("Time to plot:", round(time()-start, 2), "s")
print("Total Time taken:", round(time()-start_total, 3), "s")

plt.show()
plt.close()