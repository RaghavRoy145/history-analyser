from sys import platform
from os import path, mkdir, listdir
from pathlib import Path

browser = ""
if platform != "darwin":
    while not (browser.startswith('c') or browser.startswith('f')):
        browser = (input("Choose which browser to get the history from (C for Chrome, F for Firefox): ")).lower()
elif platform == "darwin":
    while not (browser.startswith('c') or browser.startswith('f') or browser.startswith('s')):
        browser = (input("Choose which browser to get the history from (C for Chrome, F for Firefox, S for Safari): ")).lower()

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
    profiles = ["0",""]
    while path.exists(path.join(history_folder, "Profile " + str(i))):
        print("\tProfile ", i)
        profiles.append(str(i))
        i += 1
    prof = " "
    while prof not in profiles:
        prof = input("Enter profile number (0 for default): ")
    if prof == "0" or prof == "": prof = "Default"
    else: prof = "Profile " + prof
    history_path = path.join(history_folder, prof, "History")

elif browser.startswith('f'):
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

elif browser.startswith('s'):
    history_folder = path.join(Path.home(), "Library/Safari")
    history_path = path.join(history_folder, "History.db")

from sqlite3 import connect
from pandas import read_csv, DataFrame, concat, Series, set_option, reset_option, option_context
from csv import writer
import matplotlib.pyplot as plt
from shutil import copyfile
from calendar import month_name

if not path.exists("Output"): mkdir("Output")
OUTDIR = "Output"

copyfile(history_path, path.join(OUTDIR, "Copied_History"))

conn = connect(path.join(OUTDIR, "Copied_History"))
cursor = conn.cursor()
if browser.startswith('c'):
    cursor.execute("SELECT datetime(visits.visit_time/1000000-11644473600, 'unixepoch', 'localtime') as 'visit_time',urls.url from urls,visits WHERE urls.id = visits.url ORDER BY visit_time DESC")
elif browser.startswith('f'):
    cursor.execute("""select url, datetime(last_visit_date/1000000, 'unixepoch', 'localtime') as 'visit_time'
        from moz_historyvisits natural join moz_places where
        last_visit_date is not null and url  like 'http%' and title is not null""")
elif browser.startswith('s'):
    cursor.execute("""SELECT 
        datetime(visit_time + 978307200, 'unixepoch', 'localtime') as visit_time, url
        FROM 
            history_visits
        INNER JOIN 
        history_items ON
            history_items.id = history_visits.history_item
        ORDER BY 
            visit_time DESC""")
file = path.join(OUTDIR, "url_visittime.csv")

with open(file, "w", newline='') as csv_file:
        csv_writer = writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(cursor)

dataset = read_csv(file)
dataset_copy = dataset.copy()
dataset["visit_time"] = dataset["visit_time"].apply(lambda x: str(x[11:13]))
dataset = dataset.sort_values(ascending=False, by="visit_time")
times_frequency = dataset.groupby("visit_time").size()
times_only = list(times_frequency.keys())
frequency_of_times = list(times_frequency.values)

dataset["url"] = dataset["url"].str.split("/").str[2]
dataset["url"] = dataset["url"].str.replace("www.","")
dataset["url"].replace('', None, inplace=True)
dataset.dropna(subset=["url"], inplace=True)
url_frequency = dataset.groupby("url").size()
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

#graphs
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
            ha='center', va='bottom', fontsize=5, rotation="vertical")

bar2_ax.bar(times_only, frequency_of_times)
plt.sca(bar2_ax)
plt.xticks(times_only, [], rotation="vertical")
rects = bar2_ax.patches
for rect, label in zip(rects, times_only_12hours):
    height = rect.get_height()
    bar2_ax.text(rect.get_x() + rect.get_width() / 2, height - 0.2, label,
            ha='center', va='bottom', fontsize="small")
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
    bar3_ax.text(rect.get_x() + rect.get_width() / 2, height/2 - height/6, label,
            ha='center', va='bottom', fontsize="small", rotation="vertical")


plt.tight_layout()
plt.savefig(path.join(OUTDIR, "Graphs.pdf"), format="pdf")

plt.show()
plt.close()

#categorize
df = read_csv(path.join("Output", "url_frequency.csv"), names=["url", "frequency"])
category_urls = read_csv("url_categories_copy.csv", names=["category", "url"])
category_urls["url"].str.strip()
categories_only = []
urls_only = []
for url in df["url"][:-1]:
    c = category_urls[category_urls["url"] == url]
    if not c.empty:
        categories_only.append(c["category"].iloc[0])
        urls_only.append(c["url"].iloc[0])
categories = DataFrame({"category": categories_only, "url": urls_only})

categories["frequency"] = Series()
frequencies = DataFrame()
frequencies = categories.apply(lambda x: int(df.loc[x["url"] == df["url"], ["frequency"]]["frequency"]), axis=1)
categories["frequency"] = frequencies

category_frequency = (categories.groupby("category")["frequency"].sum())

frequency_percentages = []
categories = list(category_frequency.keys())
frequencies = list(category_frequency.values)
frequency_total = sum(frequencies)
frequency_percentages = [(x/frequency_total)*100 for x in frequencies]

all_categories = ("Internet_and_Telecom","Not_working","Career_and_Education","News_and_Media","Science","Gambling","Shopping","Food_and_Drink","Books_and_Literature","Autos_and_Vehicles","Pets_and_Animals","Health","Sports","Computer_and_Electronics","Reference","Arts_and_Entertainment","Beauty_and_Fitness","Adult","Games","Law_and_Government","Finance","Business_and_Industry","Recreation_and_Hobbies","People_and_Society","Home_and_Garden","Travel","Social_Media")
categories_percentages = DataFrame(columns=all_categories)
for column_name, values in categories_percentages.iteritems():
    for category in categories:
        if category == column_name:
            categories_percentages[column_name] = Series(frequency_percentages[categories.index(category)])
categories_percentages = categories_percentages.fillna(0)
categories_percentages.to_csv(path.join("Output", "category_percentage.csv"))

x = range(0, len(categories))

fig = plt.figure()
gs = fig.add_gridspec(ncols = 1, nrows = 1)
bar_ax = fig.add_subplot(gs[0,0])
bar_ax.bar(x, frequency_percentages)
plt.sca(bar_ax)
plt.xticks(x, categories, rotation="vertical")
rects = bar_ax.patches
graph_height = (fig.get_size_inches()*fig.dpi)[1]
for rect, label in zip(rects, frequency_percentages):
    label = str(int(round(label))) + "%"
    bar_ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() - 0.3, label,
            ha='center', va='bottom')
plt.tight_layout()
plt.savefig(path.join("Output", "Category_Graphs.pdf"), format="pdf")
plt.show()
plt.close()

from sklearn.naive_bayes import GaussianNB

dataset = read_csv("gender_age_dataset.csv")
dataset = dataset.fillna(0)
array = dataset.values

category_percentages = read_csv(path.join("Output", "category_percentage.csv"))
percentages = [list((category_percentages.values.tolist())[0][1:])]

X = array[:, 2:-1]
Y = array[:, 0]

alg = GaussianNB()
alg.fit(X,Y)
predictions_for_history_gender = alg.predict(percentages)
if predictions_for_history_gender == ["M"]:
    print("\nPredicted gender: Male")
elif predictions_for_history_gender == ["F"]:
    print("Predicted gender: Female")


X_age = array[:, 2:-1]
Y_age = array[:, 1]
Y_age=Y_age.astype('int')

alg_age = GaussianNB()
alg_age.fit(X_age,Y_age)
predictions_for_history_age = alg_age.predict(percentages)
print("Predicted Age:",predictions_for_history_age[0])

print("\nGraphs are saved as PDFs in the output folder")