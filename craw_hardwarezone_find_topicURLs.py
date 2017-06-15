from bs4 import BeautifulSoup
from os import path
from datetime import datetime, timedelta
import urllib2, sys, re, os, time, signal, traceback, logging, argparse, inspect

#------------ Constants and Global Varibles ---------------#
HWZ_URL_START = 'http://forums.hardwarezone.com.sg'
# HWZ_URL_PAGE = 'http://sgforums.com'
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',}
date_format = re.compile('[0-9]{1,2}[-|\/]{1}[0-9]{1,2}[-|\/]{1}[0-9]{4}')
stats_format = [re.compile('(.+?)topic(s)*,'), re.compile('(.+?)post(s)*,'), re.compile('Popularity: (.+)')]
TOPIC, POSTS, POPULARITY = [0, 1, 2]
url_visited = {}
article_counter = 1
dummy_file = open('temp.dummy','w+')
defaults = dict.fromkeys(['def_url','def_fout_combo'], dummy_file)

NAME = 0
URL = 1
MIN_LEN = 5
MAX_LEN = 100

TODAY= time.strftime("%d-%m-%Y")
yesterday = datetime.now() - timedelta(days=1)
YESTERDAY= yesterday.strftime('%d-%m-%Y')
#------------ End Constants and Global Varibles ---------------#

#-------------- Logging and Argparse  ----------------#
program = os.path.basename(sys.argv[0])
L = logging.getLogger(program)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)
L.info("Running %s" % ' '.join(sys.argv))
p = argparse.ArgumentParser()
p.add_argument("-v", "--verbose", action='store_true')
# p.add_argument("-g", "--global", dest="global_counter", help="global_counter", type=int, default=1)
# p.add_argument("-r", "--range", dest="page_range", help="page_range", type=int, default=100)
p.add_argument("-o", "--output", dest="output_path", help="output file path", default=path.abspath('outputs/hardwarezone/'))
args = p.parse_args()
verbose = args.verbose
# global_counter = args.global_counter
# page_range = args.page_range
# MAX_PAGE = global_counter + page_range
output_path = args.output_path

#------------ End Logging and Argparse ---------------#

def write_urls():

    L.info(' >>>>>>>>>>>>> Writing crawled URLs to file <<<<<<<<<<<<<<<')
    with open(path.join(output_path, 'topic_urls.hdz.txt'),'w') as furl:
        for url in url_visited.iterkeys():
            furl.write(url)
            furl.write('\n')
    L.info(' >>>>>>>>>>>>> Crawled URLs written to file <<<<<<<<<<<<<<<')
    print '--------END------------'

#-------------- signal handler  ----------------#
def handler(signum, frame):
    print '>>> !!! Signal handler called with signal %s !!! <<<'%signum
    signal.alarm(0)
    print '>>> Alarm dismissed <<<'
    print '>>> Current recursion stack depth is : %d'%len(inspect.stack())
    print '>>> Holding for 5 Seconds ...'
    time.sleep(5)
    raise RuntimeError('TOOK TOO LONG TIME VISITING PAGE')

def find_all_target_urls(start_site, fout_combo):

    fout_combo.flush()


    start_url = start_site[URL]

    defaults.update({'def_url' : start_url, 'def_fout_combo' : fout_combo})

    L.info('Visiting start site --> ' + start_url)
    try :

        fout_combo.write('<START_URL>' + start_url + '<\START_URL>\n' )

        signal.alarm(2)  # SETTING ALARM #

        req = urllib2.Request(start_url, headers=hdr)

        signal.alarm(0)  # RESETTING ALARM #
        signal.alarm(2)  # SETTING ALARM #

        page = urllib2.urlopen(req)

        signal.alarm(0)  # RESETTING ALARM #
        signal.alarm(2)  # SETTING ALARM #

        bsObj = BeautifulSoup(page, "lxml")

        signal.alarm(0)  # RESETTING ALARM #

        headers = bsObj.findAll('td',{'class':'alt1Active'})

        headers = headers[:-3]
        for header in headers:
            # stat = []
            
            signal.alarm(2)  # SETTING ALARM #
            links = header.findAll('a', {'target' : None}, href=True)
            signal.alarm(0)  # RESETTING ALARM #
            
            for l in links:
                href = l['href']
                if not HWZ_URL_START in href:
                    if not 'http://' in href:
                        topic_url = HWZ_URL_START + l['href']
                else:
                    topic_url = href
                                    
                topic_name = l.text
                L.info('Checking TOPIC_URL : ' + topic_url)
                if not url_visited.has_key(topic_url):
                    url_visited[topic_url] = "True"
                    L.info('Visiting TOPIC_URL : ' + topic_url)
                    fout_combo.write('<TOPIC_NAME>' + topic_name + '<\TOPIC_NAME>\n')
                    fout_combo.write('<TOPIC_URL>' + topic_url + '<\TOPIC_URL>\n')

    except Exception:
        traceback.print_exc()

    L.info(' >>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<')
    write_urls()

if __name__ == "__main__":

    print '--------START------------'

    global global_counter

    start_site = ('hardwarezone', HWZ_URL_START)

    try:

        signal.signal(signal.SIGALRM, handler)

        with open(path.join(output_path, start_site[NAME] + '.topic_urls.combo'), 'w+') as fout_combo:
            find_all_target_urls(start_site, fout_combo)

    except RuntimeError:
        print "Runtime Error Catched"
        sys.exit(0)

    L.info(' >>>>>>>>>>>>> ALL pages crawled <<<<<<<<<<<<<<<')

