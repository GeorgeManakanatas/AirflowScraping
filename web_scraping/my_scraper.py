import requests
import logging
import html
import random
import time
import json
from lxml import html ,etree
from bs4 import BeautifulSoup
import urllib.robotparser
from robots.my_robots import get_page, get_page_with_soup
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
    for entry in my_config.config_values['urls_to_scrape']:
        logger.info('The entry is: %s', str(entry))
        # random time delay
        # time.sleep(random.randint(10,60))
        try:
            # get the page
            request_page, page_found = get_page_with_soup(entry['url'])
            logger.info(page_found)
            #
            if page_found:
                soup = BeautifulSoup(request_page.content, 'html.parser')
                # logger.info(str(soup))
                info = soup.find(id='mw-content-text')
                entries = soup.find('div', class_='mw-changeslist oo-ui-widget oo-ui-widget-enabled mw-rcfilters-ui-changesListWrapperWidget')
                # find all h4 elements
                h4s_list = soup.find_all('h4')
                div_list = soup.find_all('div')
                logger.info('there are : %s h4s', str(len(h4s_list)))
                for h4 in h4s_list:
                    logger.info(h4)
                logger.info('there are : %s divs', str(len(div_list)))
                for div in div_list:
                    logger.info(div)
            else:
                logger.error('page %s not found', entry['url'])

        except Exception as exc:
            logger.error('Error getting website url: %s', exc)
        

            