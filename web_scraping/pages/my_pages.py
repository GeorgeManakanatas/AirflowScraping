import logging
import csv
import requests
import random
import time
from bs4 import BeautifulSoup
from logger.custom_logger import setup_custom_logger
from database.my_database import PostgresqlInterface
#
logger = logging.getLogger('scraping')
# initialize the postgres interface
interface = PostgresqlInterface()
#
def iterate_page_urls(file_path):
    # initialize the array
    articles_with_details = []
    # open the war zone file
    with open(file_path, 'r') as my_file:
        # read file
        file_reader = csv.DictReader(my_file, delimiter=',')
        # get info from each URL
        for row in file_reader:
            # spacing the time
            time.sleep(random.randint(10,60))
            logger.info('going after URL : %s',row['url'])
            article_info = page_article_details(row['url'])
            articles_with_details.append(article_info)
    #
    with open('output/new_file.txt', 'w') as my_file:
        for line in articles_with_details:
            my_file.write(line+'\n')

def page_article_details(article_url):
    # request the url
    page = requests.get(article_url)
    logger.info('got page : %s',article_url)
    # 
    soup = BeautifulSoup(page.content, 'html.parser')
    #
    title = soup.find('h1', class_='title').getText()
    dek = soup.find('h2', class_='dek').getText()
    metadata = soup.find('div', class_='article-metadata')

    temp_entry = [title, dek , str(metadata)]
    # logger.info(str(title),str(dek),metadata)
    #
    # logger.info('information!! : %s',data_string)
    return temp_entry

def get_page_urls(request_url):
    all_urls = []
    # random wait period
    time.sleep(random.randint(10,60))
    try:
        # get page
        page_cont = requests.get(request_url)
    except Exception as exc:
            logger.error('Error connecting to page : %s', exc)
            return all_urls
    try:
        # parse page
        page_soup = BeautifulSoup(page_cont.content, 'xml')
        all_elements = page_soup.findAll("loc")
        logger.info('found %s loc elements',str(len(all_elements)))
    except Exception as exc:
        logger.error('Error parsing page contents : %s', exc)
        return all_urls
    # cleanup results
    for element in all_elements:
        all_urls.append(element.getText())
    #
    return all_urls


def recursive_search_in_sitemap(sitemap_url_from_db, website_url_from_db):
    main_list = []
    main_list.append(sitemap_url_from_db)
    while len(main_list) > 0:
        request_url = str(main_list[-1])
        if 'sitemap' in request_url:
            # get page urls and append to main list
            logger.info('Sitemap found in %s , list lenght is : %s', main_list[-1], len(main_list))
            del main_list[-1]
            main_list = main_list + get_page_urls(request_url)
        else:
            #
            logger.info('Saving %s to db, list lenght : %s',request_url,str(len(main_list)))
            interface.insert_to_pages(website_url_from_db, sitemap_url_from_db, request_url.encode)
            del main_list[-1]
