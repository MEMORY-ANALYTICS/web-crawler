import csv
import requests
import gzip

CSV_URL="https://storage.googleapis.com/basedosdados-public/one-click-download/br_inmet_bdmep/estacao/data000000000000.csv.gz"

with requests.Session() as s:
    download = s.get(CSV_URL)
    with open('data000000000000.csv.gz', 'wb') as f:
        f.write(download.content)

f = gzip.open('data000000000001.csv.gz', 'rt')
file_content=f.read()

cr = csv.reader(file_content.splitlines(), delimiter=',')
my_list = list(cr)
for row in my_list:
    print(row)