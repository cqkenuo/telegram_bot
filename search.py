from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import unquote
from selenium import webdriver


def search(search_key):
    url = 'https://duckduckgo.com/?q=%s&t=h_&iax=images&ia=images&kp=-2&k1=-1' % search_key
    images = []

    driver = get_chrome_driver(url)
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

    driver.quit()

    return images


def r34(search_key, limit=20):
    url = 'https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit={}&tags={}'.format(limit, search_key)
    parsed = BeautifulSoup(site_data(url), 'lxml')
    results = parsed.find_all('post')

    images = []

    for img in results:
        images.append(img['file_url'])

    return images


def live_leak(search_term):
    url = 'https://www.liveleak.com/browse?q={}&a=list&submit=Submit'.format(search_term)
    parsed = BeautifulSoup(site_data(url), 'lxml')
    results = parsed.find_all('a')

    videos = []
    for vid in results:
        try:
            val = str(vid['href'])

            if 'liveleak' in val.lower() and 'view' in val.lower():
                videos.append(val)
        except:
            pass

    return videos


def my_bb():
    url = 'https://www.mybroadband.co.za/news'

    driver = get_chrome_driver(url)
    parsed = BeautifulSoup(str(driver.find_element_by_class_name('feed_article_container').get_attribute('innerHTML')), 'lxml')
    results = parsed.findAll('a', attrs={'class': 'post-thumbnail'})

    articles = []
    for a in results:
        try:
            val = str(a['href'])

            if 'mybroadband' in val.lower() and 'news' in val.lower():
                articles.append(val)
        except:
            pass

    driver.quit()

    return articles[0:len(articles)]


def site_data(url):
    site = urlopen(url)
    data = site.read()
    site.close()
    return data


def get_chrome_driver(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)

    return driver


def get_firefox_driver(url):
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(firefox_options=options)
    driver.get(url)

    return driver


if __name__ == "__main__":
    for i in my_bb():
        print(i)
