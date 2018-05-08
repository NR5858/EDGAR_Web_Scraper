from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin
import requests
import re
import sys
import csv

cik_or_ticker = input("Please enter CIK or ticker: ")

# Set URL to search from
FORM_TYPE = "13F-HR"
MAX_RESULTS = 100
BASE_URL = "https://www.sec.gov"
CIK_OR_TICKER_URL = "/cgi-bin/browse-edgar?action=getcompany&CIK={}" \
                    "&type={}&dateb=&owner=exclude&count={}".format(cik_or_ticker, FORM_TYPE, MAX_RESULTS)


# Connect via TCP, create session, and make request to find relevant document
target_url = urljoin(BASE_URL, CIK_OR_TICKER_URL)
session = requests.Session()
get_search_results = SoupStrainer('a', {"id": "documentsbutton"})
soup = BeautifulSoup(session.get(target_url).content, 'lxml', parse_only=get_search_results)

# Get URL of most recent result and append it to base URL
try:
    most_recent_result = soup.find('a', {"id": "documentsbutton"})["href"]
except TypeError:
    print("No results found")
    sys.exit(1)
most_recent_result = urljoin(BASE_URL, most_recent_result)

# Retrieve .xml file
get_xml_url = SoupStrainer('tr', {"class": 'blueRow'})
soup = BeautifulSoup(session.get(most_recent_result).content, 'lxml', parse_only=get_xml_url)
xml_url = soup.find_all('tr', {"class": 'blueRow'})[1].find('a')['href']
xml_url = urljoin(BASE_URL, xml_url)
soup = BeautifulSoup(session.get(xml_url).content, 'lxml')

# Accounting for different "13F-HR" formatting
pattern = re.compile(r'(\.*)infotable')

# Parse data into "output.tsv"
with open("output.tsv", "w", newline="") as output:
    for data in soup.find_all(pattern):
        holdings = [data.text]

        # Remove all newlines
        holdings = [y for x in holdings for y in x.split("\n")]

        # Remove all empty list elements
        holdings = list(filter(None, holdings))

        # Write to .tsv file
        result = csv.writer(output, delimiter="\t")
        result.writerow(holdings)
print("output.tsv updated")
