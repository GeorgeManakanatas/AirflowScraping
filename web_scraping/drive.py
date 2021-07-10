import requests
import logging
import re
import random
import time
import json
from bs4 import BeautifulSoup
import urllib.robotparser
from robots.my_robots import get_page, check_content, check_keywords
from database.my_database import PostgresqlInterface
from config import my_config
from logger.custom_logger import setup_custom_logger
from sitemaps.my_sitemap import iterate_sitemap_urls, get_all_sitemap_urls
from pages.my_pages import recursive_search_in_sitemap

# Reading config file into global variable
my_config.config_file()
# setting up scraping logger
logging_conf = my_config.config_values['thedrive']['logging_configuration']
logger = setup_custom_logger('thedrive', logging_conf)
# initialize the postgres interface
interface = PostgresqlInterface()

if my_config.config_values['initialize_db']:
    interface.init_postgresql()


if my_config.config_values['thedrive']['scrape_websites']:
    # go through all websites
    for url in my_config.config_values['thedrive']['website_urls']:
        time.sleep(random.randint(10,60))
        logger.info('Looking at : %s',url)
        # Check the page is accessible
        page_content, page_found = get_page(url)
        logger.info('page_found: %s',str(page_found))
        # Getting robots page contents if page is found
        if page_found:
            robot_page_url = url + '/robots.txt'
            logger.info('Looking at : %s',robot_page_url)
            robot_page_content, robot_page_found = get_page(robot_page_url)
            logger.info('robot_page_found: %s',str(page_found))
        # if robot page is found get info out of it
        # TODO: redo this to work with urllib.robotparser
        keyword_results = check_keywords(robot_page_content)
        # save to database
        # TODO: add column for page_found
        try:
            interface.insert_to_websites(website_url=url, has_robots_txt=robot_page_found, has_sitemap_xml=keyword_results['Sitemap'])
        except Exception as exc:
            logger.error('Error saving website url to DB: %s', exc)


if my_config.config_values['thedrive']['scrape_sitemaps']:
    # database call here to get list of all websites from DB
    website_info = interface.select_all_websites()
    # if website info false
    if not website_info:
        logger.info('Not getting sitemap info, because website table not retrieved')
    else:
        # look for new sitemap URLs and save them in databasee
        new_urls_found = get_all_sitemap_urls(website_info)
        # log the output
        if new_urls_found:
            logger.info('New sitemap urls found')
        else:
            logger.info('No new sitemap urls')


if my_config.config_values['thedrive']['scrape_pages']:
    # database call to get list of sitemap URLs
    sitemaps_info = interface.select_sitemaps_and_websites()
    random.shuffle(sitemaps_info) # shuffle the sitemaps
    # read the sitemaps one at a time
    for table_row in sitemaps_info:
        page_url_string = table_row[1]
        website_url_string = table_row[4]
        if 'https://medium.com' in table_row:
            logger.info('-----------------------------------------------\n\n %s         %s \n\n-----------------------------------------------', page_url_string, website_url_string)
            recursive_search_in_sitemap(page_url_string, website_url_string)


if my_config.config_values['thedrive']['scrape_raw_data']:
    logger.info('Getting raw data')
    all_id_page_results = interface.select_all_pages()
    # randomize pages
    random.shuffle(all_id_page_results)
    for id_page_result in all_id_page_results:
        # getting page
        logger.info('getting page : %s',id_page_result[1])
        # sleep random time
        time.sleep(random.randint(10,60))
        page_content, page_found = get_page(id_page_result[1])
        try:
            logger.info('saving page data: %s',id_page_result[1])
            interface.insert_to_page_info(id_page_result[1],page_content.encode('utf-8'))
        except Exception as exc:
            logger.warning('Error waving page data : %s', exc)

if my_config.config_values['thedrive']['check_product_prices']:
    logger.info('Getting product prices')
    # read configuration file
    with open('config/tracked_products_list.json', 'r') as prods:
        products_config = json.load(prods)
    #
    for product in products_config['items_list']:
        time.sleep(random.randint(10,60))
        page = requests.get(product['url'],headers={"User-Agent":"Defined"})
        logger.info(str(product['price_class']))
        logger.info(str(page))
        product_soup = BeautifulSoup(page.content, 'html.parser')
        price = product_soup.find('span', class_=product['price_class'])
        logger.info('The price is: '+str(price))
            