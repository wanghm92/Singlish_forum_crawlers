from bs4 import BeautifulSoup
import urllib2, sys, re, os, time, signal, traceback, logging, argparse

#------------ Constants and Global Varibles ---------------#
sgTalk = 'http://sgtalk.org/mybb/'
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',}
date_format = re.compile('[0-9]{1,2}[-|\/]{1}[0-9]{1,2}[-|\/]{1}[0-9]{4}')
url_visited = {}
NAME = 0
URL = 1
DAY = 25
MONTH = 12
YEAR = 2016
MIN_LEN = 5
MAX_LEN = 100
TODAY= '25-5-2017'
YESTERDAY= '24-5-2017'
dummy_file = open('temp.dummy','w+')
defaults = dict.fromkeys(['def_url','def_fout_combo','def_fout_full','def_fout_short'], dummy_file)
#------------ End Constants and Global Varibles ---------------#

#-------------- Logging and Argparse  ----------------#
program = os.path.basename(sys.argv[0])
L = logging.getLogger(program)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)
L.info("Running %s" % ' '.join(sys.argv))
p = argparse.ArgumentParser()
p.add_argument("-v", "--verbose", action='store_true')
args = p.parse_args()
verbose = args.verbose
#------------ End Logging and Argparse ---------------#

def write_urls():

    L.info(' >>>>>>>>>>>>> Writing crawled URLs to file <<<<<<<<<<<<<<<')
    with open('crawled_urls.txt','wa+') as furl:
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
    print '>>> Holding for 10 Seconds ...'
    time.sleep(10)
    parse(defaults['def_url'], defaults['def_fout_combo'], defaults['def_fout_full'], defaults['def_fout_short'])
    L.info(' >>>>>>>>>>>>> ALL pages crawled <<<<<<<<<<<<<<<')
    write_urls()
    sys.exit(0)

signal.signal(signal.SIGALRM, handler)
#------------ End signal handler ---------------#

def parse_page(art_url, fout_combo, fout_full, fout_short, is_first_page=False):

    post_texts = []
    post_sents = []

    # art_url = 'http://sgtalk.org/mybb/Thread-UMS-something-brewing-for-real'
    L.info("Visting Article URL --> " + art_url)
    #------------ Get post text from table ------------#
    def get_post(table):

        signal.alarm(2)
        post_body = table.find('div', {'class': 'post_body'})
        signal.alarm(0)

        for i in post_body.findAll('a'):
            if i.has_attr('href'):
                i.extract()

        return post_body.text.strip().encode('utf-8')
    #------------ END Get post text from table ------------#

    try:

        signal.alarm(2)

        req = urllib2.Request(art_url, headers=hdr)
        if verbose:
            print 'urllib2.Request Successful !'
            print req

        page = urllib2.urlopen(req)
        if verbose:
            print 'urllib2.urlopen Successful !'
            print page

        bsObj = BeautifulSoup(page, "lxml")
        posts = bsObj.find('div',id="posts")
        tables = posts.find_all_next('table',{'class': 'tborder'})[:-1]

        L.info(' >>> Finding next page ... ')
        next_page = bsObj.find('a', {'class': 'pagination_next'})

        signal.alarm(0)

        L.info('Number of posts available = %d'%len(tables))

        for table in reversed(tables):

            is_up_to_date = False

            for b in table('blockquote'):
                b.extract()

            signal.alarm(2)
            post_time = table.find('span',{'class': 'smalltext'}).string
            signal.alarm(0)

            L.info('Post Time : ' + post_time)

            if 'Today' in post_time or 'Yesterday' in post_time:
                L.info(' >>> Extracting post from Today/Yesterday <<< ')
                is_up_to_date = True
            else:
                post_date = re.search(date_format, post_time).group(0)
                day,month,year = post_date.split('-')
                if int(year) > YEAR :
                    L.info(' >>> Extracting post from Year 2017 <<< ')
                    is_up_to_date = True
                elif int(year) == YEAR:
                    if int(month) >= MONTH and int(day) > DAY:
                        L.info(' >>> Extracting post in Dec 2016 <<< ')
                        is_up_to_date = True

            if is_up_to_date:
                L.info(' >>> Contents up-to-date, writing to combo ... ')
                target_post = get_post(table)
                post_texts.append(target_post)
                fout_combo.write('<POST_DATE>' + post_time.replace('Today', TODAY).replace('Yesterday', YESTERDAY) + '<\POST_DATE>\n')
                fout_combo.write('<POST_TEXT>\n' + target_post + '\n<\POST_TEXT>\n')
            else:
                L.info(' >>> Contents in current page are outdated <<< ')
                break

        if is_first_page:
            post_texts = post_texts[:-1]

        if post_texts:
            for p in post_texts:
                if p.split('\n') == 1:
                    post_sents.append(p)
                elif p.split('\n') > 1:
                    for s in p.split('\n'):
                        if len(s) >= 2:
                            post_sents.append(s.strip())
        L.info(' >>> post_texts are split by lines <<< ')
        L.info(' >>> post_texts are being written to file ... ')

        if post_sents:
            for p in post_sents:
                fout_full.write(p)
                fout_full.write('\n')
                if MIN_LEN <= len(p.split()) <= MAX_LEN:
                    fout_short.write(p)
                    fout_short.write('\n')

        fout_combo.flush()
        fout_full.flush()
        fout_short.flush()

        if next_page:
            L.info(' >>> next page found <<< ')
            next_url = sgTalk + next_page['href']
            if not url_visited.has_key(next_url):
                url_visited[next_url] = "True"
                L.info(">>> Visting Next Page <<<")
                fout_combo.write('<URL>' + next_url + '<\URL>\n')
                parse_page(next_url, fout_combo, fout_full, fout_short)
        else:
            L.info(' >>> next page not found <<< ')

    except Exception:
        traceback.print_exc()

def parse(start_url, fout_combo, fout_full, fout_short):

    fout_combo.flush()
    fout_full.flush()
    fout_short.flush()

    defaults.update({'def_url' : start_url, 'def_fout_combo' : fout_combo,'def_fout_full' : fout_full, 'def_fout_short' : fout_short})

    try :

        L.info('Visiting start site --> ' + start_url)
        fout_combo.write('<START_URL>' + start_url + '<\START_URL>\n' )

        req = urllib2.Request(start_url, headers=hdr)
        page = urllib2.urlopen(req)
        bsObj = BeautifulSoup(page, "lxml")

        for article in bsObj.findAll('a',{'class':'subject_new'},href=True):
            art_url = sgTalk + article['href']
            L.info('Checking Page : ' + art_url)
            if not url_visited.has_key(art_url):
                url_visited[art_url] = "True"
                L.info('Visiting Page :' + art_url)
                fout_combo.write('<URL>' + art_url + '<\URL>\n')
                parse_page(art_url, fout_combo, fout_full, fout_short, is_first_page=True)
            else:
                continue

        # Go to NEXT site if exists
        next_site = bsObj.find('a', {'class': 'pagination_next'})
        if next_site:
            next_url = sgTalk + next_site['href']
            if not url_visited.has_key(next_url):
                url_visited[next_url] = "True"
                L.info(' >>> Visiting next start site  --> ' + start_url)
                parse(next_url, fout_combo, fout_full, fout_short)

    except Exception:
        traceback.print_exc()


if __name__ == "__main__":

    print '--------START------------'

    start_sites = [
        # ('Market-Talk', 'http://sgtalk.org/mybb/Forum-Market-Talk'),
        # ('EDMW', 'http://sgtalk.org/mybb/Forum-EDMW')
        # ('Tips-for-Life', 'http://sgtalk.org/mybb/Forum-Tips-for-Life'),
        # ('Health', 'http://sgtalk.org/mybb/Forum-Health'),
        ('Property_131', 'http://sgtalk.org/mybb/Forum-Property?page=131'),
        # ('Gadgets', 'http://sgtalk.org/mybb/Forum-Gadgets'),
        # ('Daily-News', 'http://sgtalk.org/mybb/Forum-Daily-News')
    ]

    for start_site in start_sites:
        with open(start_site[NAME] + '.combo', 'w+') as fout_combo, open(start_site[NAME] + '.txt', 'w+') as fout_full, open(start_site[NAME] + '.5to50.txt', 'w+') as fout_short:
            parse(start_site[URL], fout_combo, fout_full, fout_short)

    L.info(' >>>>>>>>>>>>> ALL pages crawled <<<<<<<<<<<<<<<')

