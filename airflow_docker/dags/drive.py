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


if my_config.config_values['generic_scraper']['initialize_db']:
    interface.init_postgresql()


if my_config.config_values['generic_scraper']['check_tracked_values']:
    logger.info('Getting product values')
    for entry in my_config.config_values['generic_scraper']['urls_to_scrape']:
        logger.info('The entry is: %s', str(entry))
        # random time delay
        # time.sleep(random.randint(10,60))
        try:
            # get the page
            request_page, page_found = get_page_with_soup(entry['url'])
            logger.info(page_found)
            #
            if page_found:
                # parse with BeautifulSoup
                soup = BeautifulSoup(request_page.content, 'html.parser')
                # create pretty content
                prettyHTML = soup.prettify("utf-8")
                # save contents to file to avoid spamming site during dev
                with open('generated_resources/pages/rawHTML.txt', 'wb') as file:
                    file.write(prettyHTML)
            else:
                logger.error('page %s not found', entry['url'])

        except Exception as exc:
            logger.error('Error getting website url: %s', exc)

# read content from file
with open('generated_resources/pages/rawHTML.txt', 'r') as file:
    content = file.read()
# parse with BeautifulSoup
soup = BeautifulSoup(content, 'html.parser')
# get content text section
content_text = soup.find(id='mw-content-text')
# logger.info('content_text : %s', str(content_text))

# parse the content_text part of the page
soup = BeautifulSoup(str(content_text), 'html.parser')
page_options = soup.find_all('span', class_='oo-ui-labelElement-label')
logger.info('page_options : %s', str(page_options))
#
entries = soup.find_all('div', class_='mw-collapsible mw-collapsed mw-enhanced-rc mw-changeslist-line mw-changeslist-edit mw-changeslist-ns3000-Koppeling_IoT-peilsensordata_naar_andere_IoT-_stacks mw-changeslist-line-not-watched mw-made-collapsible')
logger.info('entries length: %s', str(len(entries)))
logger.info('entries : %s', str(entries))
soup = BeautifulSoup(str(entries), 'html.parser')
# logger.info('entries_soup: %s', str(entries))
#
h4s_list = soup.find_all('h4')
div_list = soup.find_all('div')
#
logger.info('there are : %s h4s', str(len(h4s_list)))
for h4 in h4s_list:
    logger.info(h4)
logger.info('there are : %s divs', str(len(div_list)))
for div in div_list:
    logger.info(div)

        

            