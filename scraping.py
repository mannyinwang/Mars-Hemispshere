# Dependencies
# Import Splinter, BeautifulSoup and Pandas
import pandas as pd
from bs4 import BeautifulSoup as soup
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import datetime as dt
import json


def scrape_all():
    # Setting up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}

    # Initiate headless driver for deployment
    # Setting the browser
    browser = Browser('chrome', **executable_path)

    news_title, news_summary = mars_news(browser)

    data = {
        'news_title': news_title,
        'news_summary': news_summary,
        'featured_image': featured_image(browser),
        'facts': mars_fact(),
        'mars_hemisphere': mars_hemisphere(browser),
        'last_modified': dt.datetime.now()
    }

    browser.quit()
    return data


def mars_news(browser):
    # Assign the URL
    url = 'https://mars.nasa.gov/news'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('ul.item_list li.slide', wait_time=1)

    # Setting up HTML Parser
    html = browser.html
    news = soup(html, 'html.parser')

    try:
        # Getting the news title
        slide_element = news.select_one('ul.item_list li.slide')
        news_title = slide_element.find('div', class_='content_title').get_text()

        # Getting the news summary
        news_summary = slide_element.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_summary


def featured_image(browser):
    # Visit the images url
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_element = browser.find_by_id('full_image')
    full_image_element.click()

    # Find the 'more info' button and click it
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Setting up the HTML Parser
    html = browser.html
    img = soup(html, 'html.parser')

    try:
        # Finding the relative image url
        img_url_rel = img.select_one('figure.lede a img').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL path
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    return img_url


def mars_fact():
    try:
        url = 'https://space-facts.com/mars/'
        df = pd.read_html(url, flavor='lxml')[0]

    except BaseException:
        return None

    df.columns = ['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Converting the dataframe to html
    return df.to_html(classes="table table-striped")


def mars_hemisphere(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Create a list for the values
    hemisphere_image_urls = []

    links = browser.find_by_css('a.product-item h3')
    try:
        for link in range(len(links)):
            # Create an empty dictionary
            hemisphere = {}

            browser.find_by_css('a.product-item h3')[link].click()

            # Getting the Image URL by selecting the first
            sample_element = browser.links.find_by_text('Sample').first
            hemisphere['img_url'] = sample_element['href']

            # Getting the title
            hemisphere['title'] = browser.find_by_css('h2.title').text

            # Appending the dictionary to the list
            hemisphere_image_urls.append(hemisphere)

            # Going back to the former page
            browser.back()

    except BaseException:
        return None

    return hemisphere_image_urls


if __name__ == '__main__':
    print(scrape_all())

