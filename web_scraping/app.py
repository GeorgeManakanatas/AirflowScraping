import requests
import logging
import selenium
import random
import time
import json
import urllib.robotparser
from lxml import etree
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException
from robots.my_robots import get_page, get_page_with_soup
from database.my_database import PostgresqlInterface
from config import my_config
from logger.custom_logger import setup_custom_logger

# Reading config file into global variable
my_config.config_file()
# setting up scraping logger
logger = setup_custom_logger('scraping')
# initialize the postgres interface



if my_config.config_values['scrape_vloca']:
  logger.info('Getting vloca pages')

  pages = {
      "KortePaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:KortePaginas",
      "MeestVerwezenPaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:MeestVerwezenPaginas",
      "Categorieen":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:Categorie%C3%ABn",
      "Weespaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/index.php?title=Speciaal:Weespaginas&limit=500&offset=0",
      "Termen_en_Concepten":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Categorie:Termen_en_Concepten",
      "Standaarden":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Categorie:Standaarden",
      "Technische_principes":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Categorie:Technische_principes"
  }

  difficult_pages = {
    "RecenteWijzigingen":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:RecenteWijzigingen?hidenewpages=1&hidelog=1&limit=500&days=7&enhanced=1&urlversion=2",
  }

  # for key in pages:
  #   print(key)
  #   print(pages[key])
  #   # scraping
  #   time.sleep(random.randint(1,3))
  #   page = requests.get(pages[key], verify=False)
  #   # soup = BeautifulSoup(page.content, 'html.parser')
  #   with open('output/'+key+'.html', 'wb') as file:
  #     file.write(page.content)

  opts = webdriver.ChromeOptions()
  opts.headless = True
  driver = webdriver.Chrome(ChromeDriverManager().install())
  
  for key in difficult_pages:
    # scraping
    time.sleep(random.randint(1,3))
    driver.get(difficult_pages[key])
    time.sleep(random.randint(1,3))
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    # soup = BeautifulSoup(page.content, 'html.parser')
    with open('output/'+key+'.html', 'w') as file:
      file.write(html)

  # with open('output/KortePaginas.html', 'r') as file:
  #   KortePaginas = file.read()

  # doc = etree.fromstring(KortePaginas, parser=etree.HTMLParser())
  # pages_list = doc.xpath('/html/body/div[3]/div[2]/div[3]/div/ol//li/a[2]')
  # print(len(pages_list))
  # for elem in pages_list:
  #   print(elem.attrib['href'])

  # with open('output/MeestVerwezenPaginas.html', 'r') as file:
  #   MeestVerwezenPaginas = file.read()

  # doc = etree.fromstring(MeestVerwezenPaginas, parser=etree.HTMLParser())
  # pages_list = doc.xpath('/html/body/div[3]/div[2]/div[3]/div/ol//li/a[2]')
  # print(len(pages_list))
  # for elem in pages_list:
  #   print(elem.attrib['href'])
  #   print(elem.text)

  with open('output/RecenteWijzigingen.html', 'r') as file:
    RecenteWijzigingen = file.read()

  soup = BeautifulSoup(RecenteWijzigingen, 'html.parser')
  changes_list = soup.find_all("td", class_="mw-changeslist-line-inner")
  print(len(changes_list))
  for change in changes_list:
    title = change.find("a", class_="mw-changeslist-title")
    nmbr_of_changes = change.find("a", class_="mw-changeslist-groupdiff")
    person = change.find("a", class_="new mw-userlink").find("bdi")
    print(title.getText())
    print(nmbr_of_changes.getText())
    print(person.getText())
