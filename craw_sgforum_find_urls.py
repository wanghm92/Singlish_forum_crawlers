from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import urllib2, sys, re, os, time, signal, traceback, logging, argparse, inspect

#------------ Constants and Global Varibles ---------------#
SGFORUMS_URL_START = 'http://sgforums.com/forums'
SGFORUMS_URL_PAGE = 'http://sgforums.com'
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
p.add_argument("-g", "--global", dest="global_counter", help="global_counter", type=int, default=1)
p.add_argument("-r", "--range", dest="page_range", help="page_range", type=int, default=100)
p.add_argument("-o", "--output", dest="output_path", help="output file path", default=path.abspath('outputs/sgforum/'))
args = p.parse_args()
verbose = args.verbose
global_counter = args.global_counter
page_range = args.page_range
MAX_PAGE = global_counter + page_range
output_path = args.output_path

#------------ End Logging and Argparse ---------------#

def write_urls():

    L.info(' >>>>>>>>>>>>> Writing crawled URLs to file <<<<<<<<<<<<<<<')
    with open(path.join(output_path, 'target_urls.txt'),'wa+') as furl:
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

    global global_counter

    while global_counter <= MAX_PAGE:

        start_url = start_site[URL] + '?page=%d'%global_counter

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

            headers = bsObj.findAll('li',{'class':'forum clearfix'})

            for header in headers:
                stat = []

                signal.alarm(2)  # SETTING ALARM #
                stats = header.find('div',{'class':'stats'})
                signal.alarm(0)  # RESETTING ALARM #
                
                signal.alarm(2)  # SETTING ALARM #
                title = header.find('a', {'class':'title'}, href=True)
                signal.alarm(0)  # RESETTING ALARM #
                
                art_url = SGFORUMS_URL_PAGE + title['href']
                
                for line, form in zip(stats.string.strip().split('\n'), stats_format):
                    stat.append(float(re.search(form, line).group(1).strip().replace(',','')))
                
                if stat[TOPIC] > 1 and stat[POSTS] > 1:

                    L.info('Checking TOPIC_URL : ' + art_url)
                    if not url_visited.has_key(art_url):
                        url_visited[art_url] = "True"
                        L.info('Visiting TOPIC_URL : ' + art_url)
                        fout_combo.write('<TOPIC_URL>' + art_url + '<\TOPIC_URL>\n')

                else:
                    L.info('Page has NO valuable contents : ' + art_url)

            global_counter += 1

            L.info(' >>> FINISHED start site --> ' + start_url)

        except Exception:
            traceback.print_exc()

    L.info(' >>>>>>>>>>>>> ALL pages crawled <<<<<<<<<<<<<<<')
    write_urls()

if __name__ == "__main__":

    print '--------START------------'

    global global_counter

    start_site = ('SgForums', SGFORUMS_URL_START)

    try:

        signal.signal(signal.SIGALRM, handler)

        with open(path.join(output_path, start_site[NAME] + '.urlcombo'), 'w+') as fout_combo:
            find_all_target_urls(start_site, fout_combo)

    except RuntimeError:
        print "Runtime Error Catched"
        sys.exit(0)

    L.info(' >>>>>>>>>>>>> ALL pages crawled <<<<<<<<<<<<<<<')

