from pandas import read_csv, DataFrame, concat, Series, set_option, reset_option
import pandas
from os import path
import matplotlib.pyplot as plt
from time import time
start_total = time()

df = read_csv(path.join("Output", "url_frequency.csv"), names=["url", "frequency"])
category_urls = read_csv("url_categories_copy.csv", names=["category", "url"])
#categories = DataFrame(columns=["category", "url"])

categories_only = []
urls_only = []
start = time()
for url in df["url"][:-1]:
    c = category_urls[category_urls["url"] == url] #.str.contains(str(url))
    if not c.empty:# and len(str(url)) > 5:
        categories_only.append(c["category"].iloc[0])
        urls_only.append(c["url"].iloc[0])
        #categories = concat([categories, c])
categories = DataFrame({"category": categories_only, "url": urls_only})
print("Time to concat:", round(time()-start, 2))

start = time()
#print(categories)
categories["frequency"] = Series()
frequencies = DataFrame()
#categories["frequency"]
#print(int(df.loc["stackoverflow.com" == df["url"], ["frequency"]]["frequency"]))
frequencies = categories.apply(lambda x: int(df.loc[x["url"] == df["url"], ["frequency"]]["frequency"]), axis=1)
categories["frequency"] = frequencies

category_frequency = (categories.groupby("category")["frequency"].sum())
#print((category_frequency))
print("Time to categorize:", round(time()-start, 2))

start = time()
frequency_percentages = []
categories = list(category_frequency.keys())
frequencies = list(category_frequency.values)
frequency_total = sum(frequencies)
frequency_percentages = [(x/frequency_total)*100 for x in frequencies]
print("Time to get categories, frequency and percentages:", round(time()-start, 2))

all_categories = ("Internet_and_Telecom","Not_working","Career_and_Education","News_and_Media","Science","Gambling","Shopping","Food_and_Drink","Books_and_Literature","Autos_and_Vehicles","Pets_and_Animals","Health","Sports","Computer_and_Electronics","Reference","Arts_and_Entertainment","Beauty_and_Fitness","Adult","Games","Law_and_Government","Finance","Business_and_Industry","Recreation_and_Hobbies","People_and_Society","Home_and_Garden","Travel","Social_Media")
categories_percentages = DataFrame(columns=all_categories)
for column_name, values in categories_percentages.iteritems():
    for category in categories:
        if category == column_name:
            categories_percentages[column_name] = Series(frequency_percentages[categories.index(category)])
categories_percentages = categories_percentages.fillna(0)
categories_percentages.to_csv(path.join("Output", "category_percentage.csv"))

x = range(0, len(categories))

start = time()
fig = plt.figure()
gs = fig.add_gridspec(ncols = 1, nrows = 1)
bar_ax = fig.add_subplot(gs[0,0])
bar_ax.bar(x, frequency_percentages)
plt.sca(bar_ax)
plt.xticks(x, categories, rotation="vertical")
rects = bar_ax.patches
for rect, label in zip(rects, frequency_percentages):
    label = str(int(round(label))) + "%"
    bar_ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height(), label,
            ha='center', va='bottom')
plt.tight_layout()
plt.savefig(path.join("Output", "Category_Graphs.pdf"), format="pdf")
print("Time to plot:", round(time()-start, 2))
print("Total time taken:", round(time()-start_total, 3))
plt.show()
plt.close()

with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
    print(categories_percentages)