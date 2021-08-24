from config import my_config
from bs4 import BeautifulSoup
import requests
import logging

# Reading config file into global variable
my_config.config_file()
# setting up scraping logger
logger = logging.getLogger('scraping')


def check_keywords(robot_page_content):
    '''
    Checks the robot page for specific keywords
    Parametres:
        robot_page_content (str): the contents of robots.txt
    '''
    # Initialize dictionary
    keywords = {}
    # look for keywords in robots.txt
    for keyword in my_config.config_values['thedrive']['robots_keywords']:
        # check each word
        if check_content(robot_page_content,keyword):
            keywords[keyword] = True 
        else:
            keywords[keyword] = False
    return keywords

def check_content(contents, string_value):
    '''
    Detect if substring is in a given string
    Partameters:
        contents (str): The string we look in
        string_value (str): The string we want to find
    
    Returns:
        Boolean: True if foungd False if not
    '''
    # check if strting is in the page
    if string_value in contents:
        return True
    else: 
        return False

def get_page(page_url):
    '''
    Checks is page returns 200 code and if so retreives content

    Partameters:
        page_url (str): The page url
    
    Returns:
        Str: The page contnets or null
        Bool : True if code is 200, False if anythong else
    '''
    #
    logger.info('Checking access for page : %s',page_url)
    #
    try:
        # making request to page
        request_page = requests.get(page_url)
        logger.info(request_page)
        # working with the reply
        if request_page.status_code == 200:
            logger.info('Return code 200 for : %s',page_url)
            request_page = request_page.content.decode()
            logger.info('Page content is:\n\n %s \n\n', str(request_page))
            return request_page, True
        else:
            logger.warning('Retun code not 200 for : %s', page_url)
            return 'null', False
    except Exception as exc:
            logger.error('Error accessing the page: %s', exc)


def get_page_with_soup(page_url):
    '''
    Checks is page returns 200 code and if so retreives content

    Partameters:
        page_url (str): The page url
    
    Returns:
        Str: The page contnets or null
        Bool : True if code is 200, False if anythong else
    '''
    #
    logger.info('Checking access for page : %s',page_url)
    #
    try:
        # making request to page
        request_page = requests.get(page_url)
        logger.info(request_page)
        # working with the reply
        if request_page.status_code == 200:
            logger.info('Return code 200 for : %s',page_url)
            return request_page, True
        else:
            logger.warning('Retun code not 200 for : %s', page_url)
            return 'null', False
    except Exception as exc:
            logger.error('Error accessing the page: %s', exc)
