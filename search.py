from urllib.request import urlopen
from bs4 import BeautifulSoup
from log import config
from urllib.parse import unquote
from selenium import webdriver

API_KEY = config['gapi_key']


def search(search_key):
    url = 'https://duckduckgo.com/?q=%s&t=h_&iax=images&ia=images&kp=-2&k1=-1' % search_key
    images = []

    options = webdriver.ChromeOptions()
    # options.add_argument('window-size=1680×1050')
    options.add_argument('headless')

    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)

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

    return images


def r34(search_key, limit=20):
    url = 'https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit={}&tags={}'.format(limit, search_key)
    site = urlopen(url)
    data = site.read()

    parsed = BeautifulSoup(data, 'lxml')
    results = parsed.find_all('post')

    images = []

    for img in results:
        # print(img['file_url'])
        images.append(img['file_url'])

    return images


if __name__ == "__main__":
    for i in r34("lick"):
        print(i)
