#!/usr/bin/python

import urllib.request
import logging
import html2text
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize # needs punkt package from nltk
from urllib.parse import urlparse
from urllib.parse import urljoin
import re

PROJECTNAME = "Adjutant"
VERSION = "0.1"
REPOSITORY_URL = "https://github.com/jd7h/adjutant"

TIMEOUT = 60 #seconds

def get_webpage(url):
    logging.debug("Request for %s", url)
    try:
        conn = urllib.request.urlopen(
            urllib.request.Request(url, headers={
                'User-Agent': PROJECTNAME + "/" + VERSION + ", " + REPOSITORY_URL}),timeout=TIMEOUT)
    except Exception as e:
        logging.error("%s error for %s",type(e),url)
        logging.error("repr(e) = %s",repr(e))
    return conn

def extract_html(conn):
    logging.debug("Decoding contents of %s",conn.geturl())
    try:
        if conn.headers.get_content_charset() is None:
            content = conn.read().decode()
        else:
            content = conn.read().decode(conn.headers.get_content_charset())
    except Exception as e:
        logging.error("Read error for %s: %s",conn.geturl(),type(e))
        logging.debug("repr(e) = %s",repr(e))
        return ""

def html2plaintext(html):
  text = re.sub("(<!--.*?-->)", "", text, flags=re.MULTILINE)	// comments
  text = re.sub("<script.*?\/script>","",text) // javascript
  text = re.sub("(<[^>]+>)", "", text, flags=re.MULTILINE) // html tags
  text = re.sub("\r","\n",text) // unify newlines
  text = re.sub("[\W]*\n[\W]*","\n",text)
  return text

def make_wordlist(text):
    return word_tokenize(text.lower()) # word_tokenize from nltk
    # dit gaat nog fout voor emailadressen

def count_words(words_from_content): # words_from_content is een lijst
    counted_wordlist = {}
    for word in words_from_content:
        if word not in counted_wordlist.keys():
            counted_wordlist[word] = 1
        else:
            counted_wordlist[word] += 1
    return counted_wordlist

def remove_common_words(counted_wordlist, common_words):
    for word in common_words:
        if word in counted_wordlist.keys():
            counted_wordlist.pop(word)
    return counted_wordlist


def sort_wordlist(counted_wordlist):
    return sorted(counted_wordlist.items(), key=lambda x: x[1], reverse=True)
    

def __main__(url,n,internal=True):
    # todo: process arguments
    processed_urls = []
    processed_pages = []
    text = process_page(url,n,processed_urls,processed_pages,internal)
    sorted_wordlist = create_list_from_corpus(text)
    # report
    if len(sorted_wordlist) > n:
        print(sorted_wordlist[:n+1])
    else:
        print(sorted_wordlist)
    return sorted_wordlist

def create_list_from_corpus(text):
    # make wordlist
    wordlist = make_wordlist(text)
    # count words
    counted_list = count_words(wordlist)
    # remove common words
    common_words = ["wij"] + list("!?/\@#$%^&*()-_=+.>,<;:'\"[]{}") + stopwords.words('english') + stopwords.words('dutch')
    counted_list = remove_common_words(counted_list, common_words)
    sorted_wordlist = sort_wordlist(counted_list)
    return sorted_wordlist

def getdomain(url):
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain

# note: www.website.com and website.com are different domains. :/
def find_links(url,html,only_internal):
    soup = BeautifulSoup(html,'html.parser')
    alist = soup.findAll("a")
    if not only_internal:
        return [urljoin(url,a.get("href")) for a in alist]
    else:
        targetdomain = getdomain(url)
        links = [urljoin(url,a.get("href")) for a in alist]
        return [link for link in links if getdomain(link) == targetdomain]

# note: exclude already searched pages!
def process_page(url,n,processed_urls,processed_pages,internal):
    print("Processing page:",url,"with depth",n)
    if url in processed_urls:
        print("Url already processed.")
        return ""
    else:
        # download webpage
        conn = get_webpage(url)
        html = extract_html(url, conn)
        if html in processed_pages:
            processed_urls.append(url)
            print("Page contents already processed.")
            return ""
        # extract text
        text = extract_text(html)
        processed_urls.append(url)
        processed_pages.append(html)
        children = []
        # crawl webpage with depth n
        if n > 1:
            print("links:",find_links)
            for linked_page in find_links(url,html,internal):
                child = process_page(linked_page,n-1,processed_urls,processed_pages,internal)
                children.append(child)
        return text + " ".join(children)
    

def test(url):
    # download webpage
    conn = get_webpage(url)
    # todo: crawl webpage
    # extract text
    html = extract_html(url, conn)
    text = extract_text(html)
    return html, text
