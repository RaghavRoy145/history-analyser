from time import perf_counter as time
start_total = time()
from sys import platform
from os import path, mkdir, listdir
from pathlib import Path

browser = (input("Choose which browser to get the history from (C for Chrome, F for Firefox): ")).lower()

if browser.startswith('c'):
    if platform.startswith("win"):
        history_folder = path.join(Path.home(),"AppData\\Local\\Google\\Chrome\\User Data")
    elif platform=="linux":
        history_folder = path.join(Path.home(), ".config/google-chrome")
    elif platform=="darwin":
        history_folder = path.join(Path.home(), "Library/Application Support/Google/Chrome/")
    else:
        print("Unsupported OS")
        quit()
    print("Profiles available:\n\tDefault")
    i = 1
    while path.exists(path.join(history_folder, "Profile " + str(i))):
        print("\tProfile ", i)
        i += 1
    prof = input("Enter profile number (0 for default): ")
    start = time()
    if prof == "0" or prof == "": prof = "Default"
    else: prof = "Profile " + prof
    history_path = path.join(history_folder, prof, "History")

elif browser.startswith('f'):
    start = time()
    if platform.startswith("win"):
        history_folder = path.join(Path.home(),"AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
    elif platform=="linux":
        history_folder = path.join(Path.home(), ".mozilla/firefox")
    elif platform=="darwin":
        history_folder = path.join(Path.home(), "Library/Application Support/Firefox/Profiles")
    else:
        print("Unsupported OS")
        quit()
    history_path = path.join(history_folder, [i for i in listdir(history_folder) if i.endswith('.default')][0], "places.sqlite")
    
from sqlite3 import connect
from pandas import read_csv
from csv import writer
import matplotlib.pyplot as plt
from shutil import copyfile
from calendar import month_name

if not path.exists("Output"): mkdir("Output")
OUTDIR = "Output"

copyfile(history_path, path.join(OUTDIR, "Copied_History"))
print("Time to import and copy history:", round(time()-start, 2), "s")

start = time()
conn = connect(path.join(OUTDIR, "Copied_History"))
cursor = conn.cursor()
if browser.startswith('c'):
    cursor.execute("SELECT datetime(visits.visit_time/1000000-11644473600, 'unixepoch', 'localtime') as 'visit_time',urls.url from urls,visits WHERE urls.id = visits.url ORDER BY visit_time DESC")
elif browser.startswith('f'):
    cursor.execute("""select url, datetime(last_visit_date/1000000, 'unixepoch', 'localtime') as 'visit_time'
        from moz_historyvisits natural join moz_places where
        last_visit_date is not null and url  like 'http%' and title is not null""")
file = path.join(OUTDIR, "url_visittime.csv")

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
url_frequency.to_csv(path.join(OUTDIR, "url_frequency.csv"))
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
months = [month_name[int(x[5:])] + " " + x[:4] for x in month_years]
for rect, label in zip(rects, months):
    height = rect.get_height()
    bar3_ax.text(rect.get_x() + rect.get_width() / 2, height/2 - height/10, label,
            ha='center', va='bottom', fontsize="small", rotation="vertical")


plt.tight_layout()
plt.savefig(path.join(OUTDIR, "Graphs.pdf"), format="pdf")

print("Time to plot:", round(time()-start, 2), "s")
print("Total Time taken:", round(time()-start_total, 3), "s")

plt.show()
plt.close()