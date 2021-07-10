import requests
from bs4 import BeautifulSoup
import re
import os
import time
import random
import logging
from database.my_database import PostgresqlInterface
from config import my_config
from robots.my_robots import get_page, check_content
#
logger = logging.getLogger('scraping')
#
interface = PostgresqlInterface()

def all_sitemap_urls_from_robots(robot_page_content):
    '''
    Get all sitemap related urls form robots page

    Parameters:
        robot_page_content (str): the robot.txt page contnet

    Returns:
        List: all the sitemap URLs found in the page
    '''
    # TODO: fix this so it visits robots.txt direct and gets sitemaps with urllib.robotparser
    URL_REGULAR_EXPRESSION = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    all_urls = []
    # split the robots.txt in lines to start the process
    robot_lines = robot_page_content.splitlines()
    # go over all lines and build list of sitemaps URLs found
    for line in robot_lines:
        # check if sitemaps is present in the lins
        if check_content(line, my_config.config_values['thedrive']['robots_keywords'][0]):
            # for true get the urls
            urls = re.findall(URL_REGULAR_EXPRESSION, line)
            for url in urls:
                #append to array
                all_urls.append(url)
    # return the array
    return all_urls


def get_all_sitemap_urls(website_info):
    '''
    Looking at all robot pages and finding if there are new entries to make

    Parameters:
        website_info (str): website table

    Returns:
        Boolean: True if new entries, False otherwise
    '''
    # getting all sitemap URLs from DB
    db_sitemap_urls = interface.select_all_sitemaps()
    # initialize new entry detector
    new_db_entries = False
    #looping through the all the robot pages
    for webpage_url in website_info:
        robots_web_url = webpage_url[1] + '/robots.txt'
        robot_page_content, robot_page_found = get_page(robots_web_url)
        logger.info('robot_page_found : %s',str(robot_page_found))
        # if robots page found
        if robot_page_found:
            # get list of all sitemap urls in a specific robots page
            list_of_urls = all_sitemap_urls_from_robots(robot_page_content)
            # loop through urls and check if they already exist
            for url in list_of_urls:
                # check if url exists
                if not url in [line[1] for line in db_sitemap_urls]:
                    logger.info('inserting URL : %s to database', url)
                    try:
                        interface.insert_to_sitemaps(webpage_url[1],url)
                        new_db_entries = True
                    except Exception as exc:
                        logger.error('Error saving sitemap url to DB: %s', exc)
        else:
            logger.info('Not getting sitemap info, because %s not retrieved',robots_web_url)
    # get new list and return that if any where added
    return new_db_entries

def iterate_sitemap_urls(website,sitemap_urls):
    '''
    Go over all sitemap urls and find the pages 
    '''
    # TODO: This needs to be completely redone to handle a 2 tier system
    # iterate through each url of the sitemap
    for item in sitemap_urls:
        # be nice to the site and don't spam
        time.sleep(random.randint(10,60))
        logger.info('requesting url : %s',item.strip("'"))
        get_sitemap_page = requests.get(item.strip("'"))
        xml_soup = BeautifulSoup(get_sitemap_page.content, 'xml')
        get_all_listed_urls = xml_soup.find_all('url')
        # randomize this list as well
        random.shuffle(get_all_listed_urls)
        # iterate through that list and get the war zone articles
        for article in get_all_listed_urls:
            try:     
                location = article.find('loc').getText()
                last_mod = article.find('lastmod').getText()
            except Exception as exc:
                logger.error('Error parsing location and date: %s', exc)
            try:
                interface.insert_to_pages(website,item,location)
            except Exception as exc:
                logger.error('Error saving page url to DB: %s', exc)
    return


