from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import urllib2, sys, re, os, time, signal, traceback, logging, argparse, inspect

#------------ Constants and Global Varibles ---------------#
sgTalk = 'http://sgtalk.org/mybb/'
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',}
date_format = re.compile('[0-9]{1,2}[-|\/]{1}[0-9]{1,2}[-|\/]{1}[0-9]{4}')
url_visited = {}
article_counter = 1
dummy_file = open('temp.dummy','w+')
defaults = dict.fromkeys(['def_url','def_fout_combo','def_fout_full','def_fout_short'], dummy_file)

NAME = 0
URL = 1
DAY = 25
MONTH = 12
YEAR = 2016
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
args = p.parse_args()
verbose = args.verbose
global_counter = args.global_counter
page_range = args.page_range
MAX_PAGE = global_counter + page_range

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
    print '>>> Current recursion stack depth is : %d'%len(inspect.stack())
    print '>>> Holding for 5 Seconds ...'
    time.sleep(5)
    raise RuntimeError('TOOK TOO LONG TIME VISITING PAGE')
    # parse(defaults['def_url'], defaults['def_fout_combo'], defaults['def_fout_full'], defaults['def_fout_short'])
    # L.info(' >>>>>>>>>>>>> ALL pages crawled <<<<<<<<<<<<<<<')
    # write_urls()
    # sys.exit(0)

#------------ End signal handler ---------------#

def parse_page_control(art_url, fout_combo, fout_full, fout_short, fout_old, is_first_page=False):

    global article_counter
    article_counter = 1

    print '>>> Current recursion stack depth is : %d'%len(inspect.stack())

    try:

        signal.alarm(2) # SETTING ALARM #

        req = urllib2.Request(art_url, headers=hdr)
        if verbose:
            print 'urllib2.Request Successful !'
            print req

        signal.alarm(0) # RESETTING ALARM #
        signal.alarm(2) # SETTING ALARM #

        page = urllib2.urlopen(req)
        if verbose:
            print 'urllib2.urlopen Successful !'
            print page

        signal.alarm(0) # RESETTING ALARM #
        signal.alarm(2) # SETTING ALARM #

        bsObj = BeautifulSoup(page, "lxml")

        L.info(' >>> Finding last page ... ')
        last_page = bsObj.find('a', {'class': 'pagination_last'})

        signal.alarm(0) # RESETTING ALARM #

        if last_page:
            L.info(' >>> LAST page found <<< ')
            num_pages = int(last_page['href'].split('page=')[1])
            L.info(' >>> Total number pages in this article = %d'%num_pages)
        else:
            L.info(' >>> LAST page NOT found <<< ')
            L.info(' >>> Search for LAST page ... ')

            signal.alarm(2) # SETTING ALARM #
            all_pages = bsObj.findAll('a', {'class': 'pagination_page'})
            signal.alarm(0) # RESETTING ALARM #

            if all_pages:
                num_pages = max([int(p['href'].split('page=')[1]) for p in all_pages])
            else:
                num_pages = 1
            L.info(' >>> Total number pages in this article = %d'%num_pages)

        while article_counter <= num_pages:
            print '>>> Current recursion stack depth is : %d' % len(inspect.stack())
            sub_url = art_url + '?page=%d'%article_counter
            if not url_visited.has_key(sub_url):
                L.info("Visting Article URL --> " + sub_url)
                fout_combo.write('<URL>' + sub_url + '<\URL>\n')
                parse_page(sub_url, fout_combo, fout_full, fout_short, fout_old, is_first_page)
            article_counter += 1

    except Exception:
        traceback.print_exc()

def parse_page(art_url, fout_combo, fout_full, fout_short, fout_old, is_first_page=False):

    post_texts_all = []
    post_texts_fresh = []
    post_sents_all = []
    post_sents_fresh = []

    print '>>> Current recursion stack depth is : %d'%len(inspect.stack())

    #------------ Get post text from table ------------#
    def get_post(table):

        signal.alarm(2) # SETTING ALARM #
        post_body = table.find('div', {'class': 'post_body'})
        signal.alarm(0) # RESETTING ALARM #

        for i in post_body.findAll('a'):
            if i.has_attr('href'):
                i.extract()

        return post_body.text.strip().encode('utf-8')
    #------------ END Get post text from table ------------#

    #------------ Split posts by line ------------#

    def split_by_lines(post_texts):

        post_sents = []

        for p in post_texts:
            if p.split('\n') == 1:
                post_sents.append(p)
            elif p.split('\n') > 1:
                for s in p.split('\n'):
                    if len(s) >= 2:
                        post_sents.append(s.strip())

        return post_sents

    # ------------ END Split posts by line ------------#

    try:

        signal.alarm(2) # SETTING ALARM #

        req = urllib2.Request(art_url, headers=hdr)
        if verbose:
            print 'urllib2.Request Successful !'
            print req

        signal.alarm(0) # RESETTING ALARM #
        signal.alarm(2) # SETTING ALARM #

        page = urllib2.urlopen(req)
        if verbose:
            print 'urllib2.urlopen Successful !'
            print page

        signal.alarm(0) # RESETTING ALARM #
        signal.alarm(2) # SETTING ALARM #

        bsObj = BeautifulSoup(page, "lxml")

        signal.alarm(0) # RESETTING ALARM #

        posts = bsObj.find('div', id="posts")
        tables = posts.find_all_next('table', {'class': 'tborder'})[:-1]

        L.info('Number of posts available = %d'%len(tables))

        for table in tables:

            is_up_to_date = False

            for b in table('blockquote'):
                b.extract()

            signal.alarm(2)
            post_time = table.find('span',{'class': 'smalltext'}).string
            signal.alarm(0)

            if verbose:
                L.info('Post Time : ' + post_time)

            if 'Today' in post_time or 'Yesterday' in post_time:
                if verbose:
                    L.info(' >>> Extracting post from Today/Yesterday <<< ')
                post_time.replace('Today', TODAY).replace('Yesterday', YESTERDAY)
                is_up_to_date = True
            else:
                post_date = re.search(date_format, post_time).group(0)
                day,month,year = post_date.split('-')
                if int(year) > YEAR :
                    if verbose:
                        L.info(' >>> Extracting post from Year 2017 <<< ')
                    is_up_to_date = True
                elif int(year) == YEAR:
                    if int(month) >= MONTH and int(day) > DAY:
                        if verbose:
                            L.info(' >>> Extracting post in Dec 2016 <<< ')
                        is_up_to_date = True

            target_post = get_post(table)
            post_texts_all.append(target_post)

            if is_up_to_date:
                post_texts_fresh.append(target_post)
                if verbose:
                    L.info(' >>> Contents up-to-date, writing to combo ... ')
                fout_combo.write('<POST_DATE>' + post_time + '<\POST_DATE>\n')
                fout_combo.write('<POST_TEXT>\n' + target_post + '\n<\POST_TEXT>\n')
            else:
                if verbose:
                    L.info(' >>> Contents outdated, writing to combo ... ')
                fout_combo.write('<POST_DATE>' + post_time + '<\POST_DATE>\n')
                fout_combo.write('<POST_OLD_TEXT>\n' + target_post + '\n<\PPOST_OLD_TEXT>\n')

        if is_first_page:
            L.info(' >>> Removing initial post <<< ')
            post_texts_all = post_texts_all[:-1]
            if post_texts_fresh:
                post_texts_fresh = post_texts_fresh[:-1]

        if post_texts_all:
            L.info(' >>> Splitting all posts by sents <<< ')
            post_sents_all = split_by_lines(post_texts_all)
            if post_sents_all:
                L.info(' >>> All posts are being written to file ... <<< ')
                for p in post_sents_all:
                    fout_old.write(p)
                    fout_old.write('\n')

        if post_texts_fresh:
            L.info(' >>> Splitting fresh posts by sents <<< ')
            post_sents_fresh = split_by_lines(post_texts_fresh)
            if post_sents_fresh:
                L.info(' >>> Fresh posts are being written to file ... <<< ')
                for p in post_sents_fresh:
                    fout_full.write(p)
                    fout_full.write('\n')
                    if MIN_LEN <= len(p.split()) <= MAX_LEN:
                        fout_short.write(p)
                        fout_short.write('\n')

        L.info(' >>> post_texts are being written to file ... ')

        fout_combo.flush()
        fout_full.flush()
        fout_short.flush()
        fout_old.flush()

    except Exception:
        traceback.print_exc()

def parse(start_site, fout_combo, fout_full, fout_short, fout_old):

    fout_combo.flush()
    fout_full.flush()
    fout_short.flush()
    fout_old.flush()

    global global_counter
    global article_counter

    article_counter = 1

    while global_counter <= MAX_PAGE:

        start_url = start_site[URL] + '?page=%d'%global_counter

        global_counter += 1

        defaults.update({'def_url' : start_url, 'def_fout_combo' : fout_combo,'def_fout_full' : fout_full, 'def_fout_short' : fout_short, 'def_fout_old' : fout_old})

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

            for article in bsObj.findAll('a',{'class':'subject_new'},href=True):
                art_url = sgTalk + article['href']
                L.info('Checking Page : ' + art_url)
                if not url_visited.has_key(art_url):
                    url_visited[art_url] = "True"
                    L.info('Visiting Page : ' + art_url)
                    fout_combo.write('<URL>' + art_url + '<\URL>\n')
                    parse_page_control(art_url, fout_combo, fout_full, fout_short, fout_old, is_first_page=True)
                else:
                    L.info('Page has been visited before : ' + art_url)

                    continue
            L.info(' >>> FINISHED start site --> ' + start_url)

        except Exception:
            traceback.print_exc()

    L.info(' >>>>>>>>>>>>> ALL pages crawled <<<<<<<<<<<<<<<')
    write_urls()
    sys.exit(0)

if __name__ == "__main__":

    print '--------START------------'

    global global_counter

    # start_site = ('Market-Talk-%d'%global_counter, 'http://sgtalk.org/mybb/Forum-Market-Talk')
    # start_site = ('Daily-News', 'http://sgtalk.org/mybb/Forum-Daily-News')
    # start_site = ('EDMW-%d'%global_counter, 'http://sgtalk.org/mybb/Forum-EDMW')
    # start_site = ('Tips-for-Life', 'http://sgtalk.org/mybb/Forum-Tips-for-Life')
    # start_site = ('Health', 'http://sgtalk.org/mybb/Forum-Health')
    start_site = ('Property-%d'%global_counter, 'http://sgtalk.org/mybb/Forum-Property')
    # start_site = ('Gadgets', 'http://sgtalk.org/mybb/Forum-Gadgets')

    try:

        signal.signal(signal.SIGALRM, handler)

        with open(start_site[NAME] + '.combo', 'w+') as fout_combo, open(start_site[NAME] + '.fresh.txt', 'w+') as fout_full, open(start_site[NAME] + '.fresh.%dto%d.txt'%(MIN_LEN,MAX_LEN), 'w+') as fout_short, open(start_site[NAME] + '.all.txt', 'w+') as fout_old:
            parse(start_site, fout_combo, fout_full, fout_short, fout_old)

    except RuntimeError:
        print "Runtime Error Catched"
        sys.exit(0)

    L.info(' >>>>>>>>>>>>> ALL pages crawled <<<<<<<<<<<<<<<')

