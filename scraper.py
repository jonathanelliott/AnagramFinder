import requests
from bs4 import BeautifulSoup

url = input("URL:")
filename = input("Filename:")
website_url = requests.get(url).text
soup = BeautifulSoup(website_url, 'lxml')

table_class = input("Table type (default 'sortable'):")
if not table_class:
    table_class = "sortable"
elif table_class[0] == 'w':
    table_class = "wikitable"
tables = soup.find_all('table', class_=table_class)
table_range = input("Which tables? (default all):")
if not table_range:
    pass
elif not ':' in table_range:
    tables = [tables[int(table_range)]]
else:
    table_start, table_end = map(int, table_range.split(':'))
    tables = tables[table_start:table_end]

row_labels = input("Row labels (default 'td'):")
if not row_labels:
    row_labels = "td"

col = int(input("Data column (zero-indexed):"))
data_form = input("First link or all text (default first link):")
if not data_form:
    data_form = "link"
    link_no = 0
elif data_form[0] == 'l':
    link_no = int(input("Link number (default first):"))
    if not link_no:
        link_no = 0
elif data_form[0] == 't':
    data_form = "text"

with open("datasets/" + filename + ".txt", 'a') as f:
    for table in tables:
        trs = table.find_all('tr')
        for tr in trs:
            tds = tr.find_all(row_labels)
            if not tds:
                continue
            try:
                data = tds[col]
            except IndexError:
                continue
            # if data.find('span', class_='flagicon'):
            #     continue
            if data_form == "link":
                try:
                    ls = data.find_all('a')[link_no]
                except IndexError:
                    continue
            else:
                ls = data
            if not ls:
                continue
            print(ls.text.strip())
            print(ls.text.strip(), file=f)

save = input("Add to datasets list?")
if save == 'y':
    name = input("Name:")
    with open("datasets/datasets.txt", 'a') as f:
        print(name + ": " + filename, file=f)
    print("Saved")
else:
    print("Not saved")
