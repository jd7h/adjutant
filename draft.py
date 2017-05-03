#!/usr/bin/python

import urllib.request
import logging
import html2text
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize # needs punkt package from nltk

PROJECTNAME = "Adjutant"
VERSION = "0.1"
REPOSITORY_URL = "https://github.com/jd7h/adjutant"

def get_webpage(url):
    try:
        logging.debug("Request for %s", url)
        conn = urllib.request.urlopen(
            urllib.request.Request(url, headers={
                'User-Agent': PROJECTNAME + "/" + VERSION + ", " + REPOSITORY_URL}),timeout=5)
    except Exception as e:
        logging.error("%s error for %s",type(e),url)
        logging.error("repr(e) = %s",repr(e))
    return conn

def extract_html(url, conn):
    try:
        logging.debug("Decoding contents of %s",url)
        if conn.headers.get_content_charset() is None:
            content = conn.read().decode()
        else:
            content = conn.read().decode(conn.headers.get_content_charset())
    except Exception as e:
        logging.error("Read error for %s: %s",url,type(e))
        logging.debug("repr(e) = %s",repr(e))
    return content

def extract_text(html):
    textmaker = html2text.HTML2Text()
    textmaker.ignore_images = True;
    textmaker.ignore_links = True;
    textmaker.ignore_emphasis = True;
    text = textmaker.handle(html)
    return text

def make_wordlist(text):
    return word_tokenize(text.lower())

def count_words(words_from_content):
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
    

def __main__(url,n):
# todo: process arguments
    # download webpage
    conn = get_webpage(url)
    # todo: crawl webpage
    # extract text
    html = extract_html(url, conn)
    text = extract_text(html)
    # make wordlist
    wordlist = make_wordlist(text)
    # count words
    counted_list = count_words(wordlist)
    # remove common words
    common_words = ["wij"] + list("!?/\@#$%^&*()-_=+.>,<;:'\"[]{}") + stopwords.words('english') + stopwords.words('dutch')
    counted_list = remove_common_words(counted_list, common_words)
    sorted_wordlist = sort_wordlist(counted_list)
    # report
    if len(sorted_wordlist) > n:
        print(sorted_wordlist[:n+1])
    else:
    	print(sorted_wordlist)
    return counted_list

def test(url):
    # download webpage
    conn = get_webpage(url)
    # todo: crawl webpage
    # extract text
    html = extract_html(url, conn)
    text = extract_text(html)
    return html, text
