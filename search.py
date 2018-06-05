from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlencode
from selenium import webdriver


def search(search_key):
    url = 'https://duckduckgo.com/?%s&t=h_&iax=images&ia=images&kp=-2&k1=-1' % urlencode({'q': search_key})
    images = []

    driver = get_chrome_driver(url)

    try:
        parsed = BeautifulSoup(str(driver.find_element_by_class_name('site-wrapper').get_attribute('innerHTML')), 'lxml')
        results = parsed.findAll('img')

        for img in results:
            try:
                val = unquote(str(img['src'])[2:])

                if str(val)[0:6].lower() != 'images':
                    continue

                images.append(str(val)[val.find('u=')+2:])
            except:
                pass
    except:
        from log import log
        log('search.py.search()', 'Unspecified exception occurred', True)
        pass

    driver.quit()

    return images


def r34(search_key, limit=20):
    url = 'https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit={}&{}'.format(limit, urlencode({'tags': search_key}))

    images = []

    try:
        parsed = BeautifulSoup(site_data(url), 'lxml')
        results = parsed.find_all('post')



        for img in results:
            images.append(img['file_url'])
    except:
        from log import log
        log('search.py.r34()', 'Unspecified exception occurred', True)
        pass

    return images


def live_leak(search_term):
    url = 'https://www.liveleak.com/browse?{}&a=list&submit=Submit'.format(urlencode({'q': search_term}))

    videos = []

    try:
        parsed = BeautifulSoup(site_data(url), 'lxml')
        results = parsed.find_all('a')


        for vid in results:
            try:
                val = str(vid['href'])

                if 'liveleak' in val.lower() and 'view' in val.lower():
                    videos.append(val)
            except:
                pass
    except:
        from log import log
        log('search.py.live_leak()', 'Unspecified exception occurred', True)
        pass

    return videos


def my_bb():
    url = 'https://www.mybroadband.co.za/news'

    driver = get_chrome_driver(url)
    articles = []

    try:
        parsed = BeautifulSoup(str(driver.find_element_by_class_name('feed_article_container').get_attribute('innerHTML')), 'lxml')
        results = parsed.findAll('a', attrs={'class': 'post-thumbnail'})

        for a in results:
            try:
                val = str(a['href'])

                if 'mybroadband' in val.lower() and 'news' in val.lower():
                    articles.append(val)
            except:
                pass
    except:
        from log import log
        log('search.py.my_bb()', 'Unspecified exception occurred', True)
        pass

    # ensure that the driver quits regardless
    driver.quit()

    return articles[0:len(articles)]


def chan():
    url = 'http://boards.4chan.org/b/'

    driver = get_chrome_driver(url)
    images = []

    try:
        parsed = BeautifulSoup(str(driver.find_element_by_class_name('board').get_attribute('innerHTML')), 'lxml')
        results = parsed.findAll('img')

        for im in results:
            try:
                val = str(im['src'])

                if 'i.4cdn' in val.lower():
                    images.append(str('https://' + val[2:]))
            except:
                pass
    except:
        from log import log
        log('search.py.my_bb()', 'Unspecified exception occurred', True)
        pass

    driver.quit()

    return images


def get_gifs(search_term):
    url = 'https://duckduckgo.com/?%s+gif&t=h_&iax=images&ia=images&kp=-2&k1=-1' % urlencode({'q': search_term})
    images = []

    driver = get_chrome_driver(url)

    try:
        parsed = BeautifulSoup(str(driver.find_element_by_class_name('site-wrapper').get_attribute('innerHTML')),
                               'lxml')
        results = parsed.findAll('img')

        for img in results:
            try:
                val = unquote(str(img['src'])[2:])

                if str(val)[0:6].lower() != 'images':
                    continue

                images.append(str(val)[val.find('u=') + 2:])
            except:
                pass
    except:
        from log import log
        log('search.py.search()', 'Unspecified exception occurred', True)
        pass

    driver.quit()

    return images


def site_data(url):
    try:
        site = urlopen(url)
        data = site.read()
        site.close()
    except:
        from log import log
        log('search.py.site_data()', 'Unspecified exception occurred', True)
        return None

    return data


def get_chrome_driver(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)

    try:
        driver.get(url)
    except:
        from log import log
        log('search.py.get_chrome_driver()', 'Unspecified error', True)
        return None

    return driver


def get_firefox_driver(url):
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(firefox_options=options)
    driver.get(url)

    return driver


if __name__ == "__main__":
    import time

    for i in get_gifs('test'):
        print(i)

    # waiting period to ensure everything closes properly
    # while True:
    #     time.sleep(0.2)
