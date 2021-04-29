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

# ======================================================================================================== 
# ACCESSING PAGES AND SAVING CONTENTS LOCALLY
# ======================================================================================================== 

if my_config.config_values['scrape_vloca']:
  logger.info('Getting vloca pages')
  
  pages = {
      "KortePaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:KortePaginas",
      "MeestVerwezenPaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:MeestVerwezenPaginas",
      "Categorieen":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:Categorie%C3%ABn",
      "Weespaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/index.php?title=Speciaal:Weespaginas&limit=500&offset=0",
      "Termen_en_Concepten":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Categorie:Termen_en_Concepten",
      "Standaarden":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Categorie:Standaarden",
      "Technische_principes":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Categorie:Technische_principes",
      "Statistieken":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:Statistieken",
      "InhoudelijkePaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/index.php?title=Speciaal:AllePaginas&hideredirects=1",
      "AllePaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:AllePaginas",
      "PopulairePaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/index.php?title=Speciaal:PopularPages&limit=500&offset=0",
      "WaterPagesHome":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Categorie:Leefomgeving-_Water_in_de_Stad"
  }
  difficult_pages = {
    "RecenteWijzigingen":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:RecenteWijzigingen?hidenewpages=1&hidelog=1&limit=500&days=7&enhanced=1&urlversion=2",
  }

  logger.info('Getting simple pages')
  for key in pages:
    logger.info('Getting '+key)
    # scraping
    time.sleep(random.randint(1,3))
    page = requests.get(pages[key], verify=False)
    # soup = BeautifulSoup(page.content, 'html.parser')
    with open('generated_resources/pages/'+key+'.html', 'wb') as file:
      file.write(page.content)

  logger.info('Starting Chrome driver for selenium')
  opts = webdriver.ChromeOptions()
  opts.headless = True
  driver = webdriver.Chrome(ChromeDriverManager().install())

  logger.info('Getting difficult pages')
  for key in difficult_pages:
    # scraping
    time.sleep(random.randint(1,3))
    driver.get(difficult_pages[key])
    time.sleep(random.randint(1,3))
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    # soup = BeautifulSoup(page.content, 'html.parser')
    with open('generated_resources/pages/'+key+'.html', 'w') as file:
      file.write(html)

# ======================================================================================================== 
# EXTRACTING INFORMATION OUT OF THE HTLM 
# ======================================================================================================== 
logger.info('Extracting the information')
stored_data = {}
# ------------------------------------------------------------------------------------
logger.info('KortePaginas')
with open('generated_resources/pages/KortePaginas.html', 'r') as file:
  KortePaginas = file.read()
# 
KortePaginasArray = []
doc = etree.fromstring(KortePaginas, parser=etree.HTMLParser())
pages_list = doc.xpath('/html/body/div[3]/div[2]/div[3]/div/ol//li/a[2]')
for elem in pages_list:
  KortePaginasArray.append(elem.attrib['href'])
stored_data["KortePaginas"] = KortePaginasArray
# ------------------------------------------------------------------------------------
logger.info('MeestVerwezenPaginas')
with open('generated_resources/pages/MeestVerwezenPaginas.html', 'r') as file:
  MeestVerwezenPaginas = file.read()
# 
stored_data["MeestVerwezenPaginas"] = {}
doc = etree.fromstring(MeestVerwezenPaginas, parser=etree.HTMLParser())
pages_list = doc.xpath('/html/body/div[3]/div[2]/div[3]/div/ol//li/a[2]')
for elem in pages_list:
  stored_data["MeestVerwezenPaginas"].update({elem.attrib['href']:elem.text})
# ------------------------------------------------------------------------------------
logger.info('RecenteWijzigingen')
with open('generated_resources/pages/RecenteWijzigingen.html', 'r') as file:
  RecenteWijzigingen = file.read()
# 
soup = BeautifulSoup(RecenteWijzigingen, 'html.parser')
# get all changed pages
changed_pages = soup.find_all("td", class_="mw-changeslist-line-inner")
ChangedPagesArray = []
for changed_page in changed_pages:
  ChangedPagesArray.append(changed_page.find("a", class_="mw-changeslist-title").getText())
total_changed_pages = len(changed_pages)  
#  get total of distinct changes
distinct_changes = soup.find_all("td", class_="mw-enhanced-rc")
total_individual_changes = len(distinct_changes)
# get total of bot edits
bot_edits = soup.find_all("abbr", class_="botedit")
total_bot_edits = len(bot_edits)
changes_total = {
  "total_changed_pages":total_changed_pages,
  "list_of_changed_pages":ChangedPagesArray,
  "total_individual_changes":total_individual_changes,
  "total_bot_edits":total_bot_edits
  }
stored_data["RecenteWijzigingen"] = changes_total
# ------------------------------------------------------------------------------------
logger.info('Weespaginas')
with open('generated_resources/pages/Weespaginas.html', 'r') as file:
  WeesPaginas = file.read()
# 
WeesPaginasArray = []
soup = BeautifulSoup(WeesPaginas, 'html.parser')
list = soup.find("ol", class_="special").find_all("li")
for page in list:
  title = page.find("a").getText()
  WeesPaginasArray.append(title)
stored_data["WeesPaginas"] = WeesPaginasArray
# ------------------------------------------------------------------------------------
logger.info('Technical principles')
with open('generated_resources/pages/Technische_principes.html', 'r') as file:
  TechnischePrincipes = file.read()
# 
TechnischePrincipesArray = []
soup = BeautifulSoup(TechnischePrincipes, 'html.parser')
list = soup.find_all("div", class_="mw-category-group")
for group in list:
  titles = group.find_all("li")
  for page in titles:
    title = page.find("a").getText()
    TechnischePrincipesArray.append(title)
stored_data["TechnischePrincipes"] = TechnischePrincipesArray
# ------------------------------------------------------------------------------------
logger.info('Standards')
with open('generated_resources/pages/Standaarden.html', 'r') as file:
  Standaards = file.read()
# 
StandaardsArray = []
soup = BeautifulSoup(Standaards, 'html.parser')
list = soup.find_all("div", class_="mw-category-group")
for group in list:
  titles = group.find_all("li")
  for page in titles:
    title = page.find("a").getText()
    StandaardsArray.append(title)
stored_data["Standaards"] = StandaardsArray
# ------------------------------------------------------------------------------------
logger.info('Terms and concepts')
with open('generated_resources/pages/Termen_en_Concepten.html', 'r') as file:
  Terms = file.read()
# 
stored_data["Terms"] = {}
soup = BeautifulSoup(Terms, 'html.parser')
list = soup.find_all("div", class_="mw-category-group")
for group in list:
  titles = group.find_all("li")
  for page in titles:
    elem = page.find("a")
    stored_data["Terms"].update({elem["title"]:elem["href"]})
# ------------------------------------------------------------------------------------
logger.info('Statistics')
with open('generated_resources/pages/Statistieken.html', 'r') as file:
  Stats = file.read()
# 
stored_data["Statistics"] = {}
soup = BeautifulSoup(Stats, 'html.parser')
table = soup.find("table", class_="wikitable mw-statistics-table")
statistics = table.find_all("tr", class_="mw-statistics-hook")
# get page numbers
entry = {table.find("tr", class_="mw-statistics-articles").find("td").find("a").getText():table.find("tr", class_="mw-statistics-articles").find("td", class_=("mw-statistics-numbers")).getText()}
stored_data["Statistics"].update(entry)
entry = {table.find("tr", class_="mw-statistics-pages").find("td").find("a").getText():table.find("tr", class_="mw-statistics-pages").find("td", class_=("mw-statistics-numbers")).getText()}
stored_data["Statistics"].update(entry)
#
for statistic in statistics:
  entry = {statistic.find("td").getText():statistic.find("td", class_=("mw-statistics-numbers")).getText()}
  stored_data["Statistics"].update(entry)
# get active, overall users
classes_to_look_for = ["mw-statistics-users-active","mw-statistics-users"]
for class_string in classes_to_look_for:
  statistic = table.find("tr", class_=class_string)
  entry = {statistic.find("td").find("a")["title"]:statistic.find("td", class_=("mw-statistics-numbers")).getText()}
  stored_data["Statistics"].update(entry)
# get bots
entry = {table.find("tr", class_="statistics-group-bot").find("td").find("a").getText():statistic.find("td", class_=("mw-statistics-numbers")).getText()}
stored_data["Statistics"].update(entry)
# ------------------------------------------------------------------------------------
logger.info('WaterPages')
with open('generated_resources/pages/WaterPagesHome.html', 'r') as file:
  WaterPages = file.read()
# 
stored_data["WaterPages"] = {}
soup = BeautifulSoup(WaterPages, 'html.parser')
pages = soup.find_all("div", class_="mw-category-group")
for page in pages:
  element = page.find("a")
  stored_data["WaterPages"].update({element["title"]:element["href"]})

# print(stored_data["KortePaginas"])
# print('\n')
# print(stored_data["MeestVerwezenPaginas"])
# print('\n')
# print(stored_data["RecenteWijzigingen"])
# print('\n')
# print(stored_data["WeesPaginas"])
# print('\n')
# print(stored_data["TechnischePrincipes"])
# print(stored_data["Standaards"])
# print(stored_data["Terms"])
# print('\n')
# print(stored_data["Statistics"])
# print('\n')
# print(stored_data["WaterPages"])
# print('\n')

# ======================================================================================================== 
# PROSCESSING THE INFORMATION
# ======================================================================================================== 
# ALARMS
user_edits_percent_of_total = 100 - round(stored_data["RecenteWijzigingen"]["total_bot_edits"]/stored_data["RecenteWijzigingen"]["total_individual_changes"],2)*100
logger.info("User edits are "+str(user_edits_percent_of_total)+"% of total")

# check active users

if int(stored_data["Statistics"]["Speciaal:ActieveGebruikers"]) == 0:
  if stored_data["RecenteWijzigingen"]["total_individual_changes"] == 0:
    logger.info("Active users and changes are 0 noone is paying attention!")
  elif stored_data["RecenteWijzigingen"]["total_individual_changes"] > 0:
    # calculate the % of changes by bots
    percent_bots = round(stored_data["RecenteWijzigingen"]["total_bot_edits"]/stored_data["RecenteWijzigingen"]["total_individual_changes"],2)*100
    if percent_bots == 100:
      logger.info("Active users are 0 but changes are made, we are bot central")
    elif percent_bots != 100:
      logger.info("Active users are 0 but changes by bots are "+str(percent_bots)+" so there is an error somewhere")

if int(stored_data["Statistics"]["Speciaal:ActieveGebruikers"]) > 0 and int(stored_data["Statistics"]["Speciaal:ActieveGebruikers"]) < 5:
  logger.info("Active users too low!")
  percent_bots = round(stored_data["RecenteWijzigingen"]["total_bot_edits"]/stored_data["RecenteWijzigingen"]["total_individual_changes"],2)*100

if percent_bots > 50:
  logger.info("Bot edits are too high!")

logger.info("This week we had: "+str(stored_data["RecenteWijzigingen"]["total_individual_changes"])+" distinct changes spread over: "+str(stored_data["RecenteWijzigingen"]["total_changed_pages"])+" pages.")
logger.info("The changes where made to the following pages :"+str(stored_data["RecenteWijzigingen"]["list_of_changed_pages"]))

content_pages_percent_of_total = round(int(stored_data["Statistics"]["Inhoudelijke pagina's"])/int(stored_data["Statistics"]["Pagina's"]),2)*100
logger.info("Content pages are "+str(content_pages_percent_of_total)+"% of the whole")

# EXCEL SHHEET
