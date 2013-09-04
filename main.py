#!/usr/bin/env python
import os
import requests
import pickle
from bs4 import BeautifulSoup

profile_tag = "oBd"

url_of_page = "https://www.odesk.com/o/profiles/browse/c/web-development/\
fb/45/hrs/0/?q=rails&page=%s"

countries = [
    'Austria',
    'Germany',
    #'United Kingdom'
]


def parse_soup(soup):
    profiles = []
    bad_profiles = []
    for profile in soup.find_all("div", {"class": profile_tag}):
        rate = float(profile.find("span", {"class": "oRate"}
                                  ).text.split("/")[0][1:])
        location = profile.find("span", {"class": "oLocation"}).text
        name = profile.find("span", {"itemprop": "name"}).text
        try:
            description = profile.p.text
        except:
            bad_profiles.append(profile)
        result = (name, rate, location)
        profiles.append(result)

    if len(bad_profiles):
        print "Bad profiles:", len(bad_profiles)

    return (profiles, bad_profiles)


def cached_url_contents(number):
    url = url_of_page % number
    if not os.path.exists("/tmp/odesk-cache/"):
        os.makedirs("/tmp/odesk-cache/")
    if os.path.exists("/tmp/odesk-cache/%s/html" % number):
        return "".join(open("/tmp/odesk-cache/%s/html" % number).readlines())
    else:
        html_doc = requests.get(url).content
        os.makedirs("/tmp/odesk-cache/%s" % number)
        with open("/tmp/odesk-cache/%s/html" % number, "w") as fp:
            fp.write(html_doc)
        return html_doc


def extract_profiles(n=385):
    profiles = []
    bad_profiles = []
    for page_number in range(1, n):
        html = cached_url_contents(page_number)
        soup = BeautifulSoup(html)
        #print soup
        parsed = parse_soup(soup)
        print len(parsed[0]), "good ones from", page_number
        for p in parsed[0]:
            profiles.append(p)
        print len(profiles), 'profiles total'
        bad_profiles.append(parsed[1])
    return profiles, bad_profiles


def load_pickle():
    pfile = "/tmp/odesk-cache/profiles.pickle"
    if os.path.exists(pfile):
        print "Loading profiles form cache..."
        return pickle.load(open(pfile))
    else:
        print "Extracting profiles... takes ~55 seconds on an 2011 MBA"
        profiles, bad_profiles = extract_profiles()
        if len(profiles):
            profiles = filter(len, profiles)
            profiles.sort(key=lambda x: x[1], reverse=True)
        pickle.dump(profiles, open(pfile, 'w'))
        return profiles

profiles = load_pickle()
profiles = filter(lambda x: x[2] in countries if
                    len(countries) else True, profiles)
for p in profiles[0:100]:
    print p
print len(profiles), "Profiles"
