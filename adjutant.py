import urllib.request
import logging
import html as htmlparser
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

PROJECTNAME = "Adjutant"
VERSION = "0.1"
REPOSITORY_URL = "https://github.com/jd7h/adjutant"

TIMEOUT = 60 #seconds

def get_webpage(url):
    """Obtain response (conn) from a url
    
    url -- url of the form "https://www.jd7h.com"
    """
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
    """Extract HTML code from a connection
    conn -- connection """
    if "text/html" not in conn.getheader("Content-Type"):
        return ""
    logging.debug("Decoding contents of %s",conn.geturl())
    try:
        if conn.headers.get_content_charset() is None:
            content = conn.read().decode()
        else:
            content = conn.read().decode(conn.headers.get_content_charset())
        return htmlparser.unescape(content)
    except Exception as e:
        logging.error("Read error for %s: %s",conn.geturl(),type(e))
        logging.error("repr(e) = %s",repr(e))
        return ""

def getdomain(url):
    """Compute the TLD from a URL, with or without prefix 'www'."""
    parsed_uri = urlparse(url)
    netloc = parsed_uri.netloc
    subdomains = netloc.split(".")
    if len(subdomains) > 1:
        netloc = ".".join(subdomains[-2:])
    return netloc

def getcompletedomain(url):
    """Compute the TLD from a URL. Returns a list with and without 'www.'"""
    netloc = getdomain(url)
    if "www." in netloc:
        return netloc, re.sub("www.","",netloc)
    else:
        return ["www." + netloc, netloc]


def find_links(url,html,only_internal):
    """Find all links in the html of a webpage. Returns a list with links.
    
    url -- a URL which will be used for matching found links to domain
    html -- Decoded HTML of this URL
    only_internal -- If this flag is set, this function only returns links within the same domain.
    """
    soup = BeautifulSoup(html,'html.parser')
    alist = soup.findAll("a")
    if not only_internal:
        return [urljoin(url,a.get("href")) for a in alist]
    else:
        targetdomain = getdomain(url)
        links = [urljoin(url,a.get("href")) for a in alist]
        return [link for link in links if getdomain(link) == targetdomain]

def html2plaintext(html):
    """Return the plaintext (what the user sees) from decoded HTML. Naive implementation: does not
    parse HTML but just removes everything between carets, comments, script and style tags.
    Removes newlines and multiple whitespace."""
    text = re.sub("\r","\n",html) # unify newlines
    text = re.sub("\n"," ",text) # newlines to space
    text = re.sub("<script.*?\/script>"," ",text) # javascript
    text = re.sub("<style.*?\/style>"," ",text) # css
    text = re.sub("(<!--.*?-->)", " ", text, flags=re.MULTILINE) # comments
    text = re.sub("(<[^>]+>)", " ", text, flags=re.MULTILINE) # html tags
    text = re.sub("[\W]+"," ",text)
    return text


def make_wordlist(text):
    """Turn a string into a list of tokens (words) with the tokenizer from nltk. Drawback:
    Optimized for text, not special text like code, emailaddresses, etc."""
    return word_tokenize(text.lower()) # word_tokenize from nltk
    # dit gaat nog fout voor emailadressen
    
def count_words(words_from_content):
    """Takes a list of words and makes a dictionary where the keys are words 
    and the values are integers, ie. frequency of occurrence."""
    counted_wordlist = {}
    for word in words_from_content:
        if word not in counted_wordlist.keys():
            counted_wordlist[word] = 1
        else:
            counted_wordlist[word] += 1
    return counted_wordlist

def remove_common_words(counted_wordlist, common_words):
    """Given a list of stopwords, removes those stopwords from the frequence dictionary counted_wordlist
    Stopwords source could be stopwords.words from nltk.corpus."""
    for word in common_words:
        if word in counted_wordlist.keys():
            counted_wordlist.pop(word)
    return counted_wordlist

stopwords = stopwords.words('english') + stopwords.words('dutch')

def sort_wordlist(counted_wordlist):
    """Given a dictionary of words (keys) and frequency (values), return a list
    of words,frequency tuples sorted by frequency, most frequent first."""
    return sorted(counted_wordlist.items(), key=lambda x: x[1], reverse=True)

print(stopwords)
dictwords = sort_wordlist(remove_common_words(count_words(wordlist),stopwords))
print(dictwords)


# In[10]:


totalwordlist = []
totalwordlist.append(wordlist)
THRESHOLD = 50
scrapelist = [link for link in scrapelist if ".jpg" not in link]
# todo make scrape() function
if len(scrapelist) > THRESHOLD :
    scrapelist = scrapelist[:THRESHOLD]
for link in scrapelist:
    print(link)
    try:
        connection = get_webpage(link)
        htmlcode = extract_html(connection)
        content = html2plaintext(htmlcode)
    except Exception as e:
        continue
    totalwordlist.append(make_wordlist(content))
print(totalwordlist)


# In[11]:


flattotalwordlist = [word for wordlist in totalwordlist for word in wordlist]
dictwords = sort_wordlist(remove_common_words(count_words(flattotalwordlist),stopwords))
dictwordsfiltered = [d for d in dictwords if len(d[0])>=3 and d[0].isalpha()] # only long words
#dictwordsfiltered = [d for d in dictwords if d[0].isalpha()] # only real words
for i in dictwordsfiltered[:51]:
    print(i)


# In[12]:


#print(hoffmanndict)
#print(foxdict)
hoffmann = [word[0] for word in hoffmanndict]
fox = [word[0] for word in foxdict]
intersect = [word[0] for word in hoffmanndict if word[0] in fox]
print(intersect)
print()
print([word for word in hoffmann if word not in intersect][:25])
print()
print([word for word in fox if word not in intersect][:25])


# In[ ]:





# In[61]:


def crawl(starturl,depth,internal,processed):
    content = []
    print("getting webpage: " + starturl)
    try:
        response = get_webpage(starturl)
        html = extract_html(response)
    except Exception as e:
        processed.append(starturl)
        return processed, []
    processed.append(starturl)
    content.append(html)
    #print(processed)
    if depth <= 0:
        return processed, content
    else:
        print("Continuing with depth " + str(depth-1) + "...")
        sublinks = find_links(starturl, html, internal)
        for link in sublinks:
            if link not in processed:
                processed2, content2 = crawl(link,depth-1,internal,processed)
                #print(processed2)
                #print(content2)
                processed = list(set(processed + processed2))
                content = content + content2
        return processed, content
    
prlist, contentlist = crawl(url,5,True,[])


# In[62]:


print(len(prlist), len(contentlist))


# In[63]:


text = ""
for html in contentlist:
    text = text + html2plaintext(html)


# In[64]:


len(text)


# In[65]:


text[:100]


# In[66]:


wordlist = make_wordlist(text)
print(wordlist)


# In[67]:


dictwords = sort_wordlist(remove_common_words(count_words(wordlist),stopwords))
dictwordsfiltered = [d for d in dictwords if len(d[0])>=3 and d[0].isalpha()] # only long words
#dictwordsfiltered = [d for d in dictwords if d[0].isalpha()] # only real words
for i in dictwordsfiltered[:51]:
    print(i)


# In[ ]:


url = "http://github.com"

conn = get_webpage(url)
print(conn)
print(conn.geturl())


html = extract_html(conn)
print(html)
print(getdomain(url))
host = getcompletedomain(url)
print(host)
linklist = find_links(url,html,False)
for link in linklist:
    print(link, getdomain(link), getdomain(link) in host)

# beter met scrapy

scrapelist = list(set([link for link in linklist if getdomain(link) in host]))
#scrapelist = list(set([link for link in linklist if urlparse(link).netloc in host]))
for link in scrapelist:
    #print(link)
    pass
    
scrapelist2 = find_links(url,html,True)
#print(scrapelist2)
difference = [link for link in scrapelist2 if link not in scrapelist]
print(difference)
difference = [link for link in scrapelist if link not in scrapelist2]
print(difference)

text = html2plaintext(html)
print(text)
wordlist = make_wordlist(text)
print(wordlist)

