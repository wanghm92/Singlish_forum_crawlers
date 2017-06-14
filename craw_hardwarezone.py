from os import path
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import urllib2, sys, re, os, time, signal, traceback, logging, argparse, inspect


def write_urls():

    L.info(' >>>>>>>>>>>>> Writing crawled URLs to file <<<<<<<<<<<<<<<')
    with open('crawled_urls.hdz.txt','wa+') as furl:
        for url in url_visited.iterkeys():
            furl.write(url)
            furl.write('\n')
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


def parse_page(page_url, fout_combo, fout_short, fout_all, is_first_page=False):

            # post_tables = bsObj.findAll('div', {'class': 'post-wrapper'})
            # for pt_tbl in post_tables:
            #     for div in pt_tbl.findAll('div', {'id': re.compile('post_message_([0-9]+)')}):
            #         print split_by_lines([div.text])
            # sys.exit(0)


    fout_combo.write('<TITLE_PAGE_URL>' + page_url + '<\TITLE_PAGE_URL>\n')

    post_texts_all = []

    if verbose:
        print '>>> Current recursion stack depth is : %d'%len(inspect.stack())

    L.info("Parsing TITLE_PAGE_URL --> " + page_url)

    #------------ Get post text from table ------------#
    def get_post(table):

        signal.alarm(2) # SETTING ALARM #
        post_body = table.find('div', {'class': 'body'})
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

        req = urllib2.Request(page_url, headers=hdr)
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

        posts = bsObj.find('ul', {'class': 'combined_posts'})
        tables = posts.findAll('li', {'class': 'combined_post clearfix'})

        L.info('Number of posts available = %d'%len(tables))

        for idx, table in enumerate(tables):

            for b in table('blockquote'):
                b.extract()

            signal.alarm(2)
            post_time = table.find('div',{'class': 'date'})
            signal.alarm(0)

            if post_time:
                post_time = post_time.abbr['title']
                L.info(' >>> [No.%2d] Post Time : '%idx + post_time)
            else:
                L.info(" >>> [No.%2d] Post Time NOT FOUND <<<"%idx)
                post_time = DUMMY_TIME

            target_post = get_post(table)
            post_texts_all.append(target_post)
            fout_combo.write('<POST_TIME>' + post_time + '<\POST_TIME>\n')
            fout_combo.write('<POST_TEXT>\n' + target_post + '\n<\POST_TEXT>\n')

        if post_texts_all:
            L.info(' >>> Splitting posts by sents <<< ')
            post_sents_all = split_by_lines(post_texts_all)
            if post_sents_all:
                L.info(' >>> Posts are being written to file ... <<< ')
                for p in post_sents_all:
                    fout_all.write(p)
                    fout_all.write('\n')
                    if MIN_LEN <= len(p.split()) <= MAX_LEN:
                        fout_short.write(p)
                        fout_short.write('\n')
        
        L.info(' >>> Post_texts are being written to file with flush() ... ')

        fout_combo.flush()
        fout_short.flush()
        fout_all.flush()

        L.info(' +++ FINISHED TITLE_PAGE_URL --> ' + page_url)

    except Exception:
        traceback.print_exc()

def parse_title(title_url, fout_combo, fout_short, fout_all):

    fout_combo.write('<TITLE_URL>' + title_url + '<\TITLE_URL>\n')

    global title_page_counter
    title_page_counter = PAGE_INIT

    if verbose:
        print '>>> Current recursion stack depth is : %d'%len(inspect.stack())

    L.info("Parsing TITLE_URL --> " + title_url)

    try:

        signal.alarm(2) # SETTING ALARM #

        req = urllib2.Request(title_url, headers=hdr)
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

        signal.alarm(2)  # SETTING ALARM #
        page_navigation = bsObj.find('div', {'class': 'pagination'})
        signal.alarm(0) # RESETTING ALARM #

        if page_navigation:
            signal.alarm(2)  # SETTING ALARM #
            all_pages = page_navigation.findAll('a', href=True)
            signal.alarm(0) # RESETTING ALARM #
            base_href = title_url.split(HWZ_URL_START)[1].split('.html')[0] + '-'
            num_pages = max([int(p['href'].split(base_href)[1].split('.html')[0]) for p in all_pages])
        else:
            num_pages = 1

        L.info(' >>> Number of pages in this title to crawl = %d'%num_pages)

        is_first_page = True
        page_url = title_url
        base_title_url = title_url.split('.html')[0]
        while title_page_counter <= num_pages:
                L.info('Checking TITLE_PAGE_URL : ' + page_url)
                if not url_visited.has_key(page_url):
                    L.info('Visiting TITLE_PAGE_URL : ' + page_url)
                    # parse_page(page_url, fout_combo, fout_short, fout_all, is_first_page=is_first_page)
                    url_visited[page_url] = "True"
                    is_first_page = False
                else:
                    L.info('TITLE_PAGE_URL has been visited before : ' + page_url)
                title_page_counter += 1
                page_url = base_title_url + '-%d.html'%title_page_counter

        L.info(' +++ FINISHED TITLE_URL --> ' + title_url)

    except Exception:
        traceback.print_exc()

def parse_title_list(global_page_url, fout_combo, fout_short, fout_all):

    fout_combo.write('<GLOBAL_PAGE_URL>' + global_page_url + '<\GLOBAL_PAGE_URL>\n')

    global title_list_counter
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

        topic_list = title_table.findAll('a', {'id': topic_list_id}, href=True)
        replies_list = title_table.findAll('td', {'class' : replies_list_class, 'title' : replies_list_title})

        try:
            assert len(topic_list) == len(replies_list)
        except AssertionError:
            print 'Topic replies missing!!!!!!'

        replies_list = [int(re.search(replies_list_title, obj.get('title')).group(1).replace(',','')) for obj in replies_list]

        num_titles = len(topic_list)

        while title_list_counter < num_titles:
            
            if verbose:
                print '>>> Current recursion stack depth is : %d' % len(inspect.stack())

            target_topic = topic_list[title_list_counter]
            topic_posts = replies_list[title_list_counter]
            if topic_posts > 0:
                L.info('%d posts to be crawled'%topic_posts)
                title_url = HWZ_URL_START + title_url['href']
                L.info('Checking TITLE_URL : ' + title_url)
                if not url_visited.has_key(title_url):
                    L.info("Visting TITLE_URL --> " + title_url)
                    parse_title(title_url, fout_combo, fout_short, fout_all)
                    url_visited[title_url] = "True"
                else:
                    L.info('TITLE_URL has been visited before : ' + title_url)

            else:
                L.info(' >>> NOBODY replies the Target Title --> NOT worthy crawled')
            title_list_counter += 1

        L.info(' +++ FINISHED GLOBAL_PAGE_URL --> ' + global_page_url)

    except Exception:
        traceback.print_exc()

def parse_topic(target_urls, fout_combo, fout_short, fout_all):

    fout_combo.flush()
    fout_short.flush()
    fout_all.flush()

    global global_counter
    global global_page_counter

    while global_counter < len(target_urls):

        global_page_counter = PAGE_INIT

        start_url = target_urls[global_counter]
        # start_url = "http://forums.hardwarezone.com.sg/house-displays-226/"

        defaults.update({'def_url' : start_url, 'def_fout_combo' : fout_combo, 'def_fout_short' : fout_short, 'def_fout_all' : fout_all})

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
                # base_href = start_url.split(HWZ_URL_START)[1].split('.html')[0] + '-'
                num_pages = max([int(p['href'].split('/index')[1].split('.html')[0]) for p in all_pages])
            else:
                num_pages = 1

            L.info(' ### Number of topic pages to crawl = %d ### '%num_pages)

            page_url = start_url
            while global_page_counter <= num_pages:
                L.info('Checking GLOBAL_PAGE_URL : ' + page_url)
                if not url_visited.has_key(page_url):
                    L.info('Visiting GLOBAL_PAGE_URL : ' + page_url)
                    parse_title_list(page_url, fout_combo, fout_short, fout_all)
                    url_visited[page_url] = "True"
                else:
                    L.info('GLOBAL_PAGE_URL has been visited before : ' + page_url)
                global_page_counter += 1
                page_url = start_url + 'index%d.html'%global_page_counter

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
    defaults = dict.fromkeys(['def_url','def_fout_combo','def_fout_short','def_fout_all'], dummy_file)

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

    start_site = ('hardwarezone-%d'%batch, HWZ_URL_START)

    try:

        signal.signal(signal.SIGALRM, handler)

        with open(path.join(output_path, 'target_urls.txt'),'r') as furl:
            all_url = furl.readlines()
            target_urls = [url.strip() for url in all_url[batch*batch_size:(batch+1)*batch_size]]

        L.info('>>>>>>>>>>>>> Crawling %d topic lists from Batch #%d : %d to %d <<<<<<<<<<<<<<<'%(len(target_urls) ,batch, batch*batch_size, (batch+1)*batch_size))

        with open(path.join(output_path, start_site[NAME] + '.combo'), 'w+') as fout_combo, open(path.join(output_path, start_site[NAME] + '.%dto%d.txt'%(MIN_LEN,MAX_LEN)), 'w+') as fout_short, open(path.join(output_path, start_site[NAME] + '.all.txt'), 'w+') as fout_all:
            parse_topic(target_urls, fout_combo, fout_short, fout_all)

    except RuntimeError:
        print "Runtime Error Catched"
        sys.exit(0)

    L.info(' >>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<')

