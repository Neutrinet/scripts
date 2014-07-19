import re
from bs4 import BeautifulSoup
from urllib2 import urlopen

soup = BeautifulSoup(urlopen("https://neutrinet.be/index.php?title=Category:Event"), "html5lib")

for url in ["https://neutrinet.be" + x["href"] for x in soup.find("div", id="mw-pages")("a")]:
    if url in {"https://neutrinet.be/index.php?title=Event:Meeting_2014/12"}:
        continue
    soup = BeautifulSoup(urlopen(url).read(), "html5lib")
    body = soup.find("div", id="mw-content-text").text
    pad_url = re.search("https://(quad)?pad.lqdn.fr/.+", body).group()
    if len(body) > 400:
        continue
    print url
