from os import path
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import urllib2, sys, re, os, time, signal, traceback, logging, argparse, inspect

def write_urls():

    global global_reply_estimate

    L.info(' >>>>>>>>>>>>> Writing crawled URLs to file <<<<<<<<<<<<<<<')
    with open('outputs/hardwarezone/title_urls.hdz.txt','wa') as furl:
        for url in url_visited.iterkeys():
            if url_visited[url] > 0:
                furl.write(url)
                furl.write('\n')
    with open('outputs/hardwarezone/global_reply_estimate.txt', 'wa') as festi:
        festi.write(str(global_reply_estimate))

    L.info(' >>>>>>>>>>>>> Crawled URLs written to file <<<<<<<<<<<<<<<')
    print '--------END------------'

#-------------- signal handler  ----------------#
def handler(signum, frame):
    global global_counter
    global global_page_counter
    print '>>> !!! Signal handler called with signal %s !!! <<<'%signum
    signal.alarm(0)
    print '>>> Alarm dismissed <<<'
    print '>>> Current recursion stack depth is : %d'%len(inspect.stack())
    print '>>> Holding for 5 Seconds ...'
    print '>>> Current Global Counter = %d'%global_counter
    print '>>> Current Global Page Counter = %d'%global_page_counter
    time.sleep(5)
    raise RuntimeError('TOOK TOO LONG TIME VISITING PAGE')

#------------ End signal handler ---------------#

def parse_title_list(global_page_url, fout_combo):

    fout_combo.write('<GLOBAL_PAGE_URL>' + global_page_url + '<\GLOBAL_PAGE_URL>\n')

    global title_list_counter
    global global_reply_estimate
    title_list_counter = COUNT_INIT
    
    if verbose:
        print '>>> Current recursion stack depth is : %d'%len(inspect.stack())

    L.info("Parsing GLOBAL_PAGE_URL --> " + global_page_url)

    try:

        signal.alarm(2) # SETTING ALARM #
        req = urllib2.Request(global_page_url, headers=hdr)
        signal.alarm(0) # RESETTING ALARM #
        if verbose:
            print 'urllib2.Request Successful !'
            print req

        signal.alarm(2) # SETTING ALARM #
        page = urllib2.urlopen(req)
        signal.alarm(0) # RESETTING ALARM #
        if verbose:
            print 'urllib2.urlopen Successful !'
            print page

        signal.alarm(2) # SETTING ALARM #
        bsObj = BeautifulSoup(page, "lxml")
        signal.alarm(0) # RESETTING ALARM #

        # title_table = bsObj.findAll('table', id='threadslist')

        signal.alarm(2) # SETTING ALARM #
        title_table = bsObj.findAll('tbody', {'id': title_table_id})
        signal.alarm(0) # RESETTING ALARM #

        try:
            assert len(title_table) == 1
            title_table = title_table[0]
        except AssertionError:
            print 'More than 1 title table found!!!!!!'

        topic_replies_list = title_table.findAll('tr')

        num_titles = len(topic_replies_list)
        L.info(' ### Number of titles to be crawled = %d '%num_titles)

        while title_list_counter < num_titles:
            
            if verbose:
                print '>>> Current recursion stack depth is : %d' % len(inspect.stack())
            
            target_tuple = topic_replies_list[title_list_counter]

            target_topic = target_tuple.find('a', {'id': topic_list_id}, href=True)
            num_of_replies = target_tuple.find('td', {'class' : replies_list_class, 'title' : replies_list_title})

            if num_of_replies:

                num_of_replies = int(re.search(replies_list_title, num_of_replies.get('title')).group(1).replace(',',''))

                if num_of_replies > 0:
                    L.info(' ### Number of replies to be crawled = %d '%num_of_replies)
                    title_url = HWZ_URL_START + target_topic['href']
                    L.info('Checking TITLE_URL : ' + title_url)
                    if not url_visited.has_key(title_url):
                        global_reply_estimate += int(num_of_replies*1.0/15+0.5)
                        L.info("Visting TITLE_URL --> " + title_url)
                        fout_combo.write('<TITLE_URL>' + title_url + '<\TITLE_URL>\n')
                        url_visited[title_url] = num_of_replies
                    else:
                        L.info('TITLE_URL has been visited before : ' + title_url)

                else:
                    L.info(' >>> NOBODY replies the Target Title --> NOT worthy crawled')
            else:
                L.info(' >>> This topic is moved away !!!')

            title_list_counter += 1

        L.info(' +++ FINISHED GLOBAL_PAGE_URL --> ' + global_page_url)
        fout_combo.flush()

    except Exception:
        traceback.print_exc()

def parse_topic(target_urls, fout_combo):

    fout_combo.flush()

    global global_counter
    global global_page_counter

    while global_counter < len(target_urls):

        global_page_counter = PAGE_INIT

        start_url = target_urls[global_counter]

        defaults.update({'def_url' : start_url, 'def_fout_combo' : fout_combo})

        L.info('Visiting GLOBAL_URL --> ' + start_url)

        try :

            fout_combo.write('<GLOBAL_URL>' + start_url + '<\GLOBAL_URL>\n' )

            signal.alarm(2)  # SETTING ALARM #

            req = urllib2.Request(start_url, headers=hdr)

            signal.alarm(0)  # RESETTING ALARM #
            signal.alarm(2)  # SETTING ALARM #

            page = urllib2.urlopen(req)

            signal.alarm(0)  # RESETTING ALARM #
            signal.alarm(2)  # SETTING ALARM #

            bsObj = BeautifulSoup(page, "lxml")

            signal.alarm(0)  # RESETTING ALARM #

            signal.alarm(2)  # SETTING ALARM #
            page_navigation = bsObj.find('div', {'class': 'pagination'})
            signal.alarm(0) # RESETTING ALARM #

            if page_navigation:
                
                signal.alarm(2)  # SETTING ALARM #
                all_pages = page_navigation.findAll('a', href=True)
                signal.alarm(0) # RESETTING ALARM #
                num_pages = max([int(p['href'].split('/index')[1].split('.html')[0]) for p in all_pages])
            else:
                num_pages = 1

            L.info(' ### Number of topic pages to crawl = %d ### '%num_pages)

            page_url = start_url
            while global_page_counter <= num_pages:
                L.info('Checking GLOBAL_PAGE_URL : ' + page_url)
                if not url_visited.has_key(page_url):
                    L.info('Visiting GLOBAL_PAGE_URL : ' + page_url)
                    parse_title_list(page_url, fout_combo)
                    url_visited[page_url] = -1
                else:
                    L.info('GLOBAL_PAGE_URL has been visited before : ' + page_url)
                global_page_counter += 1
                page_url = start_url + 'index%d.html'%global_page_counter

            L.info(' ### Current Estimated Number of Replies to crawl = %d'%global_reply_estimate)
            L.info(' +++ FINISHED GLOBAL_URL --> ' + start_url)

            global_counter += 1

        except Exception:
            traceback.print_exc()

    write_urls()
    L.info(' >>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<')
    sys.exit(0)

if __name__ == "__main__":

    print '--------START------------'

    #------------ Constants and Global Varibles ---------------#

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',}
    dummy_file = open('temp.dummy','w+')
    defaults = dict.fromkeys(['def_url','def_fout_combo'], dummy_file)

    date_format = re.compile('[0-9]{1,2}[-|\/]{1}[0-9]{1,2}[-|\/]{1}[0-9]{4}')
    stats_format = [re.compile('(.+?)topic(s)*,'), re.compile('(.+?)post(s)*,'), re.compile('Popularity: (.+)')]
    title_table_id = re.compile('threadbits_forum_([0-9]+)')
    topic_list_id = re.compile('thread_title_([0-9]+)')
    replies_list_class = re.compile('alt[1-2]')
    replies_list_title = re.compile('Replies: (.+?), Views: (.+?)')

    TOPIC, POSTS, POPULARITY = [0, 1, 2]
    NAME, URL = [0, 1]
    COUNT_INIT, PAGE_INIT = [0, 1]
    MIN_LEN, MAX_LEN = [5, 100]
    TODAY= time.strftime("%d-%m-%Y")
    yesterday = datetime.now() - timedelta(days=1)
    YESTERDAY= yesterday.strftime('%d-%m-%Y')
    HWZ_URL_START = 'http://forums.hardwarezone.com.sg'
    DUMMY_TIME = 'YYYY-MM-DDThh:mm:ss+08:00'

    url_visited = {}
    global_counter = COUNT_INIT # index of starting topic site in current batch
    global_page_counter = PAGE_INIT # page iterator for the starting topic site
    title_list_counter = COUNT_INIT # entry-title iterator in current topic site
    title_page_counter = PAGE_INIT # page iterator for current title site
    global_reply_estimate = COUNT_INIT
    #------------ End Constants and Global Varibles ---------------#

    #-------------- Logging and Argparse  ----------------#
    program = os.path.basename(sys.argv[0])
    L = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)
    L.info("Running %s" % ' '.join(sys.argv))
    p = argparse.ArgumentParser()
    p.add_argument("-v", "--verbose", action='store_true')
    p.add_argument("-b", "--batch", dest="batch", help="batch", type=int, default=0)
    p.add_argument("-s", "--batch_size", dest="batch_size", help="batch_size", type=int, default=10)
    p.add_argument("-o", "--output", dest="output_path", help="output file path", default=path.abspath('outputs/hardwarezone/'))
    args = p.parse_args()
    verbose = args.verbose
    batch = args.batch
    batch_size = args.batch_size
    output_path = args.output_path
    #------------ End Logging and Argparse ---------------#

    start_site = ('hardwarezone-Size%d-Batch%d'%(batch_size, batch), HWZ_URL_START)

    try:

        signal.signal(signal.SIGALRM, handler)

        with open(path.join(output_path, 'target_urls.txt'),'r') as furl:
            all_url = furl.readlines()
            target_urls = [url.strip() for url in all_url[batch*batch_size:(batch+1)*batch_size]]

        L.info('>>>>>>>>>>>>> Crawling %d topic lists from Batch #%d : %d to %d <<<<<<<<<<<<<<<'%(len(target_urls) ,batch, batch*batch_size, (batch+1)*batch_size))

        with open(path.join(output_path, start_site[NAME] + '.title_urls.combo'), 'w+') as fout_combo:
            parse_topic(target_urls, fout_combo)

    except RuntimeError:
        print "Runtime Error Catched"
        sys.exit(0)

    L.info(' >>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<')

