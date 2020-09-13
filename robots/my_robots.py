from config import my_config
import requests
import logging

# Reading config file into global variable
my_config.config_file()
# setting up scraping logger
logger = logging.getLogger('scraping')


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
        robot_page = requests.get(page_url)
        # working with the reply
        if robot_page.status_code == 200:
            logger.info('Return code 200 for : %s',page_url)
            robot_page_text = robot_page.content.decode()
            return robot_page_text, True
        else:
            logger.warning('Retun code not 200 for : %s', page_url)
            return null, False
    except Exception as exc:
            logger.error('Error accessing the robots page: %s', exc)
