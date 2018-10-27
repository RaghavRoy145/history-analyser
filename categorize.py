import pandas
import sys
import matplotlib.pyplot as plt

def OutputDirectory():
    if sys.platform=="win32":
        return "Output\\"
    elif sys.platform=="linux" or sys.platform=="darwin":
        return "Output/"

df = pandas.read_csv(OutputDirectory() + "url_frequency.csv", names=["url", "frequency"])
category_urls = pandas.read_csv("url_categories copy.csv", names=["category", "url"])
categories = pandas.DataFrame(columns=["category", "url"])

for url in df["url"][:-1]:
    c = category_urls[category_urls["url"] == url] #.str.contains(str(url))]
    if not c.empty and len(str(url)) > 5:
        categories = pandas.concat([categories, c])
#print(categories)
categories["frequency"] = pandas.Series()
frequencies = pandas.DataFrame()
#categories["frequency"]
#print(int(df.loc["stackoverflow.com" == df["url"], ["frequency"]]["frequency"]))
frequencies = categories.apply(lambda x: int(df.loc[x["url"] == df["url"], ["frequency"]]["frequency"]), axis=1)
categories["frequency"] = frequencies

category_frequency = (categories.groupby("category")["frequency"].sum())
print((category_frequency))

categories = []
frequencies = []
for i in category_frequency.keys():
    categories.append(i)
    frequencies.append(category_frequency[i])

x = range(0, len(categories))

plt.bar(x, frequencies)
plt.xticks(x, categories, rotation="vertical")
plt.tight_layout()
plt.savefig(OutputDirectory()+"Category_Graphs.pdf", format="pdf")
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

