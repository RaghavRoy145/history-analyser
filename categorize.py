from pandas import read_csv, DataFrame, concat, Series
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
    c = category_urls[category_urls["url"] == url] #.str.contains(str(url))]
    if not c.empty:# and len(str(url)) > 5:
        categories_only.append(c["category"].iloc[0])
        urls_only.append(c["url"].iloc[0])
        #categories = concat([categories, c])
categories = DataFrame({"category": categories_only, "url": urls_only})
print(categories)
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
categories = []
frequencies = []
frequency_percentages = []
for i in category_frequency.keys():
    categories.append(i)
    frequencies.append(category_frequency[i])
frequency_total = sum(frequencies)
frequency_percentages = [(x/frequency_total)*100 for x in frequencies]
print("Time to get categories, frequency and percentages:", round(time()-start, 2))

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

"""def get_frequency(a):
    for row in df.itertuples():
        print(a, row[1])
        if row[1] in a:
            return row[2]
        else:
            return "NA"

frequencies = categories["url"].apply(get_frequency) #lambda x : df.frequency[categories.url.str.contains(str(x))].sum(),1)
print(frequencies)"""
"""for url1 in categories["url"]:
    for url2 in df["url"]:
        if str(url2) in str(url1):
            frequencies.append(df.loc[df["url"] == url2, "frequency"].iloc[0])"""
        #categories = categories.assign(freq = df.get(url2))
#print(frequencies)
#print(len(categories))
#print(len(frequencies))
#categories = categories.assign(freq = frequencies)
"""urls = []
for url in categories["url"]:
    for url2 in df["url"]:
        if str(url2) in str(url):
            urls.append(categories[categories["url"].str.replace(str(url), str(url2))])
            categories_of_urls.append()
print(urls)
categories_of_urls = []"""

