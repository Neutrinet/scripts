import os
import re
import sys
import mechanicalsoup
from bs4 import BeautifulSoup
from urllib2 import urlopen

soup = BeautifulSoup(urlopen("http://neutrinet.be/index.php?title=Category:Event"), "html5lib")
browser = mechanicalsoup.Browser()

to_handle = []

for url in ["http://neutrinet.be" + x["href"] for x in soup.find("div", id="mw-pages")("a")]:
    if url in {"http://neutrinet.be/index.php?title=Event:Meeting_2014/12"}:
        continue
    soup = BeautifulSoup(urlopen(url).read(), "html5lib")
    body = soup.find("div", id="mw-content-text").text
    pad_url = re.search("https://(quad)?pad.lqdn.fr/.+", body).group()
    if len(body) > 400:
        continue
    to_handle.append((url, pad_url))
    break

if not to_handle:
    sys.exit(0)

# login
page = browser.get("http://neutrinet.be/index.php?title=Special:UserLogin&returnto=Main+Page")
form = page.soup.find("div", id="userloginForm").select("form")[0]

form.find("input", id="wpName1")["value"] = ""
form.find("input", id="wpPassword1")["value"] = ""

browser.submit(form, page.url)
