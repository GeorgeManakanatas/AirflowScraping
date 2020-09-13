import requests
import logging
import html
import random
import time
import json
from lxml import html
from lxml import etree
from bs4 import BeautifulSoup
import urllib.robotparser
from robots.my_robots import get_page
from database.my_database import PostgresqlInterface
from config import my_config
from logger.custom_logger import setup_custom_logger

# Reading config file into global variable
my_config.config_file()
# setting up scraping logger
logger = setup_custom_logger('scraping')
# initialize the postgres interface
interface = PostgresqlInterface()


if my_config.config_values['initialize_db']:
    interface.init_postgresql()


if my_config.config_values['check_tracked_values']:
    logger.info('Getting product values')
    # read configuration file
    with open('config/tracked_products_list.json', 'r') as prods:
        products_config = json.load(prods)
    #
    for product in products_config['items_list']:
        # random time delay
        # time.sleep(random.randint(10,60))
        try:
            # get the page
            page_content, page_found = get_page(product['url'])
            #
            if page_found:
                logger.info('Page content is: %s \n\n\n\n\n',page_content)
                product_soup = BeautifulSoup(page_content, 'html.parser')
                price = product_soup.find('span', class_=product['price_class'])
                logger.info('The price is: %s', str(price))
            else:
                logger.error('page %s not found', product['url'])

        except Exception as exc:
            logger.error('Error getting website url: %s', exc)
        

            