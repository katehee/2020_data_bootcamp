import os
import re
import time


try:
    from selenium import webdriver

except ImportError:
    print("Trying to Install required module: selenium\n")
    os.system('python -m pip install selenium')
    from selenium import webdriver

try:
    from bs4 import BeautifulSoup

except ImportError:
    print("Trying to Install required module: bs4\n")
    os.system('python -m pip install bs4')
    from bs4 import BeautifulSoup

try:
    import pandas as pd

except ImportError:
    print("Trying to Install required module: pandas\n")
    os.system('python -m pip install pandas')
    import pandas as pd


url_list = []
keyword = ['seaweed', 'snack']

# extract url
for i in range(1, 6):
    url = "https://www.amazon.com/s?k=" + keyword[0] + '+' + keyword[1] +\
          '&rh=n%3A16322721&ref=nb_sb_noss&' + 'page=' + str(i)
    driver = webdriver.Chrome("../chromedriver.exe")
    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    list_ = soup.select(
        "div.a-section.a-spacing-none.a-spacing-top-small > h2 > a.a-link-normal.a-text-normal")

    for l in list_:
        url_ = l.attrs['href']
        url_list.append("https://www.amazon.com" + url_)

    driver.close()

url_list = pd.DataFrame(data={'url_list': url_list})
url_list = url_list[~url_list['url_list'].str.contains("sp_mtf")]


# extract product info
title = []
categories = []
flavors = []
size = []
features = []
price = []

for url in url_list['url_list']:
    driver = webdriver.Chrome("../chromedriver.exe")
    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    try:
        title.append(soup.select("#productTitle")[0].text.strip('\n'))
    except:
        title.append('x')

    try:
        size.append(soup.select('span.selection')[0].text.strip('\n'))
    except:
        size.append('x')

    try:
        for li in soup.select("#wayfinding-breadcrumbs_container ul.a-unordered-list")[0].findAll("li"):
            category = li.text.strip('\n')
        categories.append(category)
    except:
        categories.append('x')

    try:
        for li in soup.select("#feature-bullets ul.a-unordered-list")[0].findAll('li'):
            feature = li.text.strip('\n')
        features.append(feature)
    except:
        features.append('x')

    try:
        price.append(soup.select("span.a-size-small.a-color-price")[0].text.strip('\n'))
    except:
        price.append('x')

    driver.close()

amazon_product_result = pd.DataFrame(data=
                                     {'title': title, 'categories': categories,
                                      'size': size, 'features': features, 'price': price}
                                     )

amazon_product_result = amazon_product_result[~amazon_product_result['title'].str.contains("3D")]


# extract review info
products = []
stars = []
authors = []
titles = []
comments = []
dates = []

for url in url_list['url_list']:
    driver = webdriver.Chrome("../chromedriver.exe")
    driver.get(url)

    try:
        product = driver.find_element_by_css_selector("#productTitle").text.strip('\n')
        content = driver.find_element_by_css_selector("a.a-link-emphasis.a-text-bold")
        content.click()

        page_source = driver.page_source
        current_url = driver.current_url
        soup = BeautifulSoup(page_source, "html.parser")
        time.sleep(0.5)

        count = soup.find("div", {"data-hook": "cr-filter-info-review-rating-count"}).text
        count = count.replace(',', '')
        a, b = count.split('|')
        counts = re.findall("\d+", b)
        number = int(counts[0]) // 10

        for page in range(1, number + 2):
            address = current_url + '&pageNumber=' + str(page)
            driver.get(address)
            time.sleep(0.5)
            ps = driver.page_source
            soup = BeautifulSoup(ps, "html.parser")

            author = soup.select(
                "div #cm_cr-review_list div.a-row.a-spacing-mini a.a-profile div.a-profile-content span.a-profile-name")
            star_rating = soup.findAll("i", {"data-hook": "review-star-rating"})
            date = soup.findAll("span", {"data-hook": "review-date"})
            title = soup.findAll("a", {"data-hook": "review-title"})
            comment = soup.findAll("span", {"data-hook": "review-body"})

            try:
                for a in author:
                    authors.append(a.text.strip('\n'))
            except:
                authors.append(None)

            try:
                for s in star_rating:
                    stars.append(s.text.strip('\n'))
            except:
                stars.append(None)

            try:
                for d in date:
                    dates.append(d.text.strip('\n'))
            except:
                dates.append(None)

            try:
                for t in title:
                    titles.append(t.text.strip('\n'))
            except:
                titles.append(None)

            try:
                for c in comment:
                    comments.append(c.text.strip('\n'))
                    try:
                        products.append(product)
                    except:
                        products.append(None)
            except:
                comments.append(None)

        driver.close()

    except:
        print("comment crawler error")
        driver.close()

length = min(len(products), len(authors), len(stars), len(dates), len(titles), len(comments))

products = products[:length]
authors = authors[:length]
stars = stars[:length]
dates = dates[:length]
titles = titles[:length]
comments = comments[:length]

amazon_comment_result = pd.DataFrame(data={'product': products, 'author': authors, 'star': stars,
                                            'date': dates, 'title': titles, 'comment': comments})

amazon_product_result.to_csv("amazon_product_data.csv", index=False)
amazon_comment_result.to_csv("amazon_comment_data.csv", index=False)
