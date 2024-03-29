"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""

import selenium
import json
import logging
import time
import requests
import random
import xlsxwriter
from collections import Counter
from lxml import etree
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# ======================================================================================================== 
# CONFIGURATION
# ======================================================================================================== 

default_args = {
	"owner": "airflow",
	"depends_on_past": False,
	"start_date": datetime(2021, 8, 31),
	"email": ["airflow@airflow.com"],
	"email_on_failure": False,
	"email_on_retry": False,
	"retries": 1,
	"retry_delay": timedelta(minutes=5),
	# 'queue': 'bash_queue',
	# 'pool': 'backfill',
	# 'priority_weight': 10,
	# 'end_date': datetime(2016, 1, 1),
}

my_config = {   
	"scrape_vloca_pages":1,
	"vloca":{
		"postgresql_connection":{
			"host":"localhost",
			"port":"5432",
			"dbname":"autoscrapedb",
			"user":"postgres",
			"password":"scrapedbpass",
			"schemaname":"scraping_info"
		},
		"logging_configuration":{
			"folder":"generated_resources/logs/",
			"filename":"vloca.log"
		}
	}
}

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
	"WaterPagesHome":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Categorie:Leefomgeving-_Water_in_de_Stad",
	"NewPages":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:NieuwePaginas?namespace=all&tagfilter=&username=&size-mode=min&size=&wpFormIdentifier=newpagesform&limit=500"
}

difficult_pages = {
	"RecenteWijzigingen":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:RecenteWijzigingen?hidenewpages=1&hidelog=1&limit=500&days=7&enhanced=1&urlversion=2",
}

# ======================================================================================================== 
# FUNCTIONS
# ======================================================================================================== 


def get_pages_request():
	if my_config['scrape_vloca_pages']:
		logging.info('Getting pages with request')
		for key in pages:
			logging.info('Getting '+key)
			# scraping
			time.sleep(random.randint(1,3))
			page = requests.get(pages[key], verify=False)
			# soup = BeautifulSoup(page.content, 'html.parser')
			with open('/usr/local/airflow/dags/generated_resources/pages/'+key+'.html', 'w', encoding="utf-8") as file:
				file.write(str(page.content))
	else:
		logging.info('scrape_vloca_pages set to false')


def get_pages_selenium():
	if my_config['scrape_vloca_pages']:
		logging.info('Starting Chrome driver for selenium')
		opts = webdriver.ChromeOptions()
		opts.add_argument('enable-automation')
		opts.add_argument('--headless')
		opts.add_argument('--no-sandbox')
		opts.add_argument('--disable-dev-shm-usage')
		opts.add_argument('--disable-extensions')
		opts.add_argument('--disable-gpu')
		opts.add_argument('--remote-debugging-port=9222')
		driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)

		logging.info('Getting difficult pages')
		for key in difficult_pages:
			# scraping
			time.sleep(random.randint(1,3))
			driver.get(difficult_pages[key])
			time.sleep(random.randint(1,3))
			html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
			# soup = BeautifulSoup(page.content, 'html.parser')
			with open('/usr/local/airflow/dags/generated_resources/pages/'+key+'.html', 'w', encoding="utf-8") as file:
				file.write(html)
	else:
		logging.info('scrape_vloca_pages set to false')


def extract_information():
	logging.info('Extracting the information')
	stored_data = {}
	# ------------------------------------------------------------------------------------
	logging.info('KortePaginas')
	with open('/usr/local/airflow/dags/generated_resources/pages/KortePaginas.html', 'r', encoding="utf-8") as file:
		KortePaginas = file.read()
	# 
	KortePaginasArray = []
	doc = etree.fromstring(KortePaginas, parser=etree.HTMLParser())
	pages_list = doc.xpath('/html/body/div[3]/div[2]/div[3]/div/ol//li/a[2]')
	for elem in pages_list:
		KortePaginasArray.append(elem.attrib['href'])
	stored_data["KortePaginas"] = KortePaginasArray
	# ------------------------------------------------------------------------------------
	logging.info('MeestVerwezenPaginas')
	with open('/usr/local/airflow/dags/generated_resources/pages/MeestVerwezenPaginas.html', 'r', encoding="utf-8") as file:
		MeestVerwezenPaginas = file.read()
	# 
	stored_data["MeestVerwezenPaginas"] = {}
	doc = etree.fromstring(MeestVerwezenPaginas, parser=etree.HTMLParser())
	pages_list = doc.xpath('/html/body/div[3]/div[2]/div[3]/div/ol//li/a[2]')
	for elem in pages_list:
		stored_data["MeestVerwezenPaginas"].update({elem.attrib['href']:elem.text})
	# ------------------------------------------------------------------------------------
	logging.info('RecenteWijzigingen')
	with open('/usr/local/airflow/dags/generated_resources/pages/RecenteWijzigingen.html', 'r', encoding="utf-8") as file:
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
	# get list of changes by person
	person_changes = soup.find_all("a", class_="new mw-userlink")
	# get counter of changes
	changes_per_person = Counter(person_changes)
	# 
	total_individual_changes = len(distinct_changes)
	# get total of bot edits
	bot_edits = soup.find_all("abbr", class_="botedit")
	total_bot_edits = len(bot_edits)
	changes_total = {
		"total_changed_pages":total_changed_pages,
		"list_of_changed_pages":ChangedPagesArray,
		"total_individual_changes":total_individual_changes,
		"total_bot_edits":total_bot_edits,
		"person_changes_number":{}
		}
	for change in changes_per_person:
		changes_total["person_changes_number"].update({change["title"]:changes_per_person.get(change)})

	stored_data["RecenteWijzigingen"] = changes_total
	# ------------------------------------------------------------------------------------
	logging.info('Weespaginas')
	with open('/usr/local/airflow/dags/generated_resources/pages/Weespaginas.html', 'r', encoding="utf-8") as file:
		WeesPaginas = file.read()
	# 
	WeesPaginasArray = []
	soup = BeautifulSoup(WeesPaginas, 'html.parser')
	# print(soup)
	content = soup.find("div", class_="mw-spcontent")
	# print(content)
	list = content.find_all("li")
	for page in list:
		title = page.find("a").getText()
		WeesPaginasArray.append(title)
	stored_data["WeesPaginas"] = WeesPaginasArray
	# ------------------------------------------------------------------------------------
	logging.info('Technical principles')
	with open('/usr/local/airflow/dags/generated_resources/pages/Technische_principes.html', 'r', encoding="utf-8") as file:
		TechnischePrincipes = file.read()
	# 
	stored_data["TechnischePrincipes"] = {} 
	soup = BeautifulSoup(TechnischePrincipes, 'html.parser')
	list = soup.find_all("div", class_="mw-category-group")
	for group in list:
		titles = group.find_all("li")
		for page in titles:
			elem = page.find("a")
			stored_data["TechnischePrincipes"].update({elem["title"]:elem["href"]})
	# ------------------------------------------------------------------------------------
	logging.info('Standards')
	with open('/usr/local/airflow/dags/generated_resources/pages/Standaarden.html', 'r', encoding="utf-8") as file:
		Standaards = file.read()
	# 
	stored_data["Standaards"] = {}
	soup = BeautifulSoup(Standaards, 'html.parser')
	list = soup.find_all("div", class_="mw-category-group")
	for group in list:
		standards = group.find_all("li")
		for page in titles:
			elem = page.find("a")
			stored_data["Standaards"].update({elem["title"]:elem["href"]})
	# ------------------------------------------------------------------------------------
	logging.info('Terms and concepts')
	with open('/usr/local/airflow/dags/generated_resources/pages/Termen_en_Concepten.html', 'r', encoding="utf-8") as file:
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
	logging.info('Statistics')
	with open('/usr/local/airflow/dags/generated_resources/pages/Statistieken.html', 'r', encoding="utf-8") as file:
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
	entry = {table.find("tr", class_="statistics-group-bot").find("td").find("a").getText():table.find("tr", class_="statistics-group-bot").find("td", class_=("mw-statistics-numbers")).getText()}
	stored_data["Statistics"].update(entry)
	# ------------------------------------------------------------------------------------
	logging.info('WaterPages')
	with open('/usr/local/airflow/dags/generated_resources/pages/WaterPagesHome.html', 'r', encoding="utf-8") as file:
		WaterPages = file.read()
	# 
	stored_data["WaterPages"] = {}
	soup = BeautifulSoup(WaterPages, 'html.parser')
	pages = soup.find_all("div", class_="mw-category-group")
	for page in pages:
		element = page.find("a")
		stored_data["WaterPages"].update({element["title"]:element["href"]})
	# ------------------------------------------------------------------------------------
	logging.info('NewPages')
	with open('/usr/local/airflow/dags/generated_resources/pages/NewPages.html', 'r', encoding="utf-8") as file:
		NewPages = file.read()
	# 
	stored_data["NewPages"] = []
	soup = BeautifulSoup(NewPages, 'html.parser')
	content = soup.find("div", id="mw-content-text").find("ul").find_all("li")
	for page in content:
		pageInfo = {}
		# pageInfo.update({"date":page.find("span", class_="mw-newpages-time").getText()})
		name_url = page.find("a", class_="mw-newpages-pagename")
		pageInfo["date"]= page.find("span", class_="mw-newpages-time").getText()
		pageInfo["url"] = str(name_url["href"])
		pageInfo["name"]= str(name_url["title"])
		pageInfo["comment"] = str(page.find("span", class_="comment").getText())
		stored_data["NewPages"].append(pageInfo)
	with open('/usr/local/airflow/dags/generated_resources/pages/stored_data.json', 'w', encoding="utf-8") as file:
		json.dump(stored_data, file, indent=2, sort_keys=True)


def proscessing_information():
	# read the stored_data
	with open('/usr/local/airflow/dags/generated_resources/pages/stored_data.json', 'r', encoding="utf-8") as file:
		stored_data = json.load(file)
	# ALARMS
	stored_data["Alarms"] = {}
	if int(stored_data["RecenteWijzigingen"]["total_individual_changes"]):
		# % of user edits edits
		user_edits_percent_of_total = 1 - round(stored_data["RecenteWijzigingen"]["total_bot_edits"]/stored_data["RecenteWijzigingen"]["total_individual_changes"],2)
		stored_data["Alarms"]["user_edits_percent_of_total"] = user_edits_percent_of_total
		logging.info("User edits are "+str(int(user_edits_percent_of_total)*100)+"% of total")
		# % of bot edits
		percent_bots = round(stored_data["RecenteWijzigingen"]["total_bot_edits"]/stored_data["RecenteWijzigingen"]["total_individual_changes"],2)
		stored_data["Alarms"]["percent_bots"] = percent_bots
	else:
		# if there are no changes then user and bot edits are 0
		user_edits_percent_of_total = 0
		percent_bots = 0
		stored_data["Alarms"]["user_edits_percent_of_total"] = 0
		stored_data["Alarms"]["percent_bots"] = 0
		logging.info("No edits to the wiki!")
	# bot edits as % of total
	bot_value = percent_bots*100
	if bot_value > 30:
		stored_data["Alarms"]["bot_traffic"] = "Bot edits are too high at "+str(bot_value)+"% of total"
	else:
		stored_data["Alarms"]["bot_traffic"] = "Bot edits are acceptable at "+str(bot_value)+"% of total"
	logging.info(stored_data["Alarms"]["bot_traffic"])
	# checks for potential red flags involving active users
	
	if int(stored_data["Statistics"]["Speciaal:ActieveGebruikers"]) == 0:
		if stored_data["RecenteWijzigingen"]["total_individual_changes"] == 0:
			stored_data["Alarms"]["check_active_users"] = "Active users and changes are 0 noone is paying attention!"
		elif stored_data["RecenteWijzigingen"]["total_individual_changes"] > 0:
			# calculate the % of changes by bots
			if bot_value == 100:
				stored_data["Alarms"]["check_active_users"] = "Active users are 0 but changes are made, we are bot central"
			elif bot_value != 100:
				stored_data["Alarms"]["check_active_users"] = "Active users are 0 but changes by bots are "+str(int(bot_value))+" so there is an error somewhere"
	logging.info(stored_data["Alarms"]["check_active_users"])
	# active vs total users
	
	if int(stored_data["Statistics"]["Speciaal:ActieveGebruikers"]) == 0:
		stored_data["Alarms"]["user_engagement"] = "0 active users we have no engagement"
	if int(stored_data["Statistics"]["Speciaal:ActieveGebruikers"]) > 0 and int(stored_data["Statistics"]["Speciaal:ActieveGebruikers"]) < 5:
		stored_data["Alarms"]["user_engagement"] = "Active users too low at less than 5!"
	logging.info(stored_data["Alarms"]["user_engagement"])
	# edits to pages
	stored_data["Alarms"]["edits_to_pages"] = "This week we had: "+str(stored_data["RecenteWijzigingen"]["total_individual_changes"])+" distinct changes spread over: "+str(stored_data["RecenteWijzigingen"]["total_changed_pages"])+" pages."
	logging.info(stored_data["Alarms"]["edits_to_pages"])
	# list of edited pages
	stored_data["Alarms"]["list_of_editied_pages"] = "The changes where made to the following pages :"+str(stored_data["RecenteWijzigingen"]["list_of_changed_pages"])
	logging.info(stored_data["Alarms"]["list_of_editied_pages"])
	# how many pages are content pages
	content_pages_percent_of_total = round(int(stored_data["Statistics"]["Inhoudelijke pagina's"])/int(stored_data["Statistics"]["Pagina's"]),2)*100
	stored_data["Alarms"]["content_pages_percent_of_total"] = content_pages_percent_of_total
	logging.info(stored_data["Alarms"]["content_pages_percent_of_total"])
	#
	logging.info("There are: "+str(len(stored_data["KortePaginas"]))+" short pages")
	logging.info("There are: "+str(len(stored_data["WeesPaginas"]))+" orphan pages out of a total of :"+str(stored_data["Statistics"]["Inhoudelijke pagina's"])+" content pages")
	#
	with open('/usr/local/airflow/dags/generated_resources/pages/stored_data.json', 'w', encoding="utf-8") as file:
		json.dump(stored_data, file, indent=2, sort_keys=True)


def checking_for_links():
	# read the stored_data
	with open('/usr/local/airflow/dags/generated_resources/pages/stored_data.json', 'r', encoding="utf-8") as file:
		stored_data = json.load(file)
	all_pages_links = {}
	for page_key in stored_data["WaterPages"]:
		# logger.info('for page: '+stored_data["WaterPages"][page_key])
		all_pages_links[page_key] = []
		# scraping
		time.sleep(random.randint(1,3))
		page = requests.get("https://vloca-kennishub.vlaanderen.be"+stored_data["WaterPages"][page_key], verify=False)
		content = str(page.content)
		for key in stored_data["Terms"]:
			# logger.info(key)
			link_string = "https://vloca-kennishub.vlaanderen.be"+stored_data["Terms"][key]+" "+key
			links_needed = {}
			# Find term
			logging.info('looking for '+key)
			if (content.find(key) != -1):
					# find link
					logging.info("Contains the term "+key)
					if (content.find(link_string) == -1):
						logging.info("Does not contain "+link_string)
						all_pages_links[page_key].append({key:link_string})
	#
	stored_data["all_pages_links"] = all_pages_links
	#
	with open('/usr/local/airflow/dags/generated_resources/pages/stored_data.json', 'w', encoding="utf-8") as file:
		json.dump(stored_data, file, indent=2, sort_keys=True)


def making_excel_file():
	#
	with open('/usr/local/airflow/dags/generated_resources/pages/stored_data.json', 'r', encoding="utf-8") as file:
		stored_data = json.load(file)
	# Create a workbook and add a worksheet.
	now = datetime.now()
	workbook_name = now.strftime("%Y_%m_%d")+"_report"
	workbook = xlsxwriter.Workbook('/usr/local/airflow/dags/generated_resources/output/'+workbook_name+'.xlsx')
	# formatting
	merge_format = workbook.add_format({
			'bold': 1,
			'border': 1,
			'align': 'center',
			'valign': 'vcenter'})

	color_format = workbook.add_format({
			'bold': 1,
			'border': 1,
			'align': 'center',
			'valign': 'vcenter',
			'fg_color': 'yellow'})

	warning_format = workbook.add_format({
			'bold': 1,
			'border': 1,
			'align': 'center',
			'valign': 'vcenter',
			'fg_color': 'red'})

	default_format = workbook.add_format({
			'align': 'center',
			'valign': 'vcenter'})
	# support functions
	def make_entry(row, col, entry, worksheet, formating=default_format):
		worksheet.write(row, col, entry, formating)

	def enter_multiple_columns(row, col, array, worksheet, formating=default_format):
		for value in array:
			worksheet.write(row, col, value, formating)
			col +=1
	#
	worksheet_GeneralInfo = workbook.add_worksheet('General Info')
	#
	array = ["Weekly edits ", stored_data["RecenteWijzigingen"]["total_individual_changes"]]
	enter_multiple_columns(1, 0, array ,worksheet_GeneralInfo)
	array = ["Edited pages count ", stored_data["RecenteWijzigingen"]["total_changed_pages"]]
	enter_multiple_columns(2, 0, array,worksheet_GeneralInfo)
	array = ["User edits", stored_data["RecenteWijzigingen"]["total_individual_changes"]]
	enter_multiple_columns(3, 0, array,worksheet_GeneralInfo)
	array = ["User edits percent of total", stored_data["Alarms"]["user_edits_percent_of_total"]]
	enter_multiple_columns(4, 0, array,worksheet_GeneralInfo)
	array = ["Bot edits", stored_data["RecenteWijzigingen"]["total_bot_edits"]]
	enter_multiple_columns(5, 0, array,worksheet_GeneralInfo)
	array = ["Bot edits percent of total", stored_data["Alarms"]["percent_bots"]]
	enter_multiple_columns(6, 0, array,worksheet_GeneralInfo)
	array = ["Active users", stored_data["Statistics"]["Speciaal:ActieveGebruikers"]]
	enter_multiple_columns(7, 0, array,worksheet_GeneralInfo)
	#
	percent_of_content = int((len(stored_data["KortePaginas"])/int(stored_data["Statistics"]["Inhoudelijke pagina's"]))*100)
	percent_of_total = int((len(stored_data["KortePaginas"])/int(stored_data["Statistics"]["Pagina's"]))*100)
	array = ["Short pages", len(stored_data["KortePaginas"]),"Percent of content pages",percent_of_content,"Percent of total",percent_of_total]
	enter_multiple_columns(8, 0, array,worksheet_GeneralInfo)
	percent_of_content = int((len(stored_data["WeesPaginas"])/int(stored_data["Statistics"]["Inhoudelijke pagina's"]))*100)
	percent_of_total = int((len(stored_data["WeesPaginas"])/int(stored_data["Statistics"]["Pagina's"]))*100)
	array = ["Orphan pages",len(stored_data["WeesPaginas"]),"Percent of content pages",percent_of_content,"Percent of total",percent_of_total]
	enter_multiple_columns(9, 0, array ,worksheet_GeneralInfo)
	worksheet_GeneralInfo.write(0, 8, "Person",color_format)
	worksheet_GeneralInfo.write(0, 9, "Changes",color_format)
	row = 1 
	# print(stored_data["RecenteWijzigingen"]["person_changes_number"])
	for entry in stored_data["RecenteWijzigingen"]["person_changes_number"]:
		make_entry(row, 8, str(entry) ,worksheet_GeneralInfo)
		make_entry(row, 9, str(stored_data["RecenteWijzigingen"]["person_changes_number"][entry]) ,worksheet_GeneralInfo)
		row += 1

	worksheet_Warnings = workbook.add_worksheet('Warnings')

	make_entry(1, 0, stored_data["Alarms"]["check_active_users"], worksheet_Warnings, warning_format)
	make_entry(2, 0, stored_data["Alarms"]["bot_traffic"], worksheet_Warnings)
	make_entry(3, 0, stored_data["Alarms"]["user_engagement"], worksheet_Warnings, warning_format)

	worksheet_lists = workbook.add_worksheet('Aggregated lists')
	make_entry(0, 0, "KortePaginas", worksheet_lists)
	row = 1
	for page in stored_data["KortePaginas"]:
		make_entry(row, 0, page, worksheet_lists)
		row += 1

	make_entry(0, 1, "WeesPaginas", worksheet_lists)
	row = 1
	for page in stored_data["WeesPaginas"]:
		make_entry(row, 1, page, worksheet_lists)
		row += 1

	make_entry(0, 2, "Standaards", worksheet_lists)
	row = 1
	for page in stored_data["Standaards"]:
		make_entry(row, 2, page, worksheet_lists)
		row += 1

	make_entry(0, 3, "Terms", worksheet_lists)
	row = 1
	for page in stored_data["Terms"]:
		make_entry(row, 3, page, worksheet_lists)
		row += 1

	make_entry(0, 4, "MeestVerwezenPaginas", worksheet_lists)
	row = 1
	for key in stored_data["MeestVerwezenPaginas"]:
		array = [key, stored_data["MeestVerwezenPaginas"][key]]
		enter_multiple_columns(row, 4, array, worksheet_lists)
		row += 1

	make_entry(0, 6, "NewPages", worksheet_lists)
	row = 1
	for entry in stored_data["NewPages"]:
		array = [entry["date"], entry["name"], entry["url"]]
		enter_multiple_columns(row, 6, array, worksheet_lists)
		row += 1

	worksheet_missing_links = workbook.add_worksheet('Missing links')

	column = 0
	for key in stored_data["all_pages_links"]:
		row = 0 
		make_entry(row, column, key, worksheet_missing_links)
		for entry in stored_data["all_pages_links"][key]:
			row += 1
			make_entry(row, column, str(entry), worksheet_missing_links)
		column += 1

	workbook.close()



# ======================================================================================================== 
# DEFINING TASKS
# ======================================================================================================== 
dag = DAG("vloca_native", default_args=default_args, schedule_interval=timedelta(1))

# get pages using request task
get_pages_request = PythonOperator(task_id="static_content", python_callable=get_pages_request, retries=1, dag=dag)
# get pages using selenium
get_pages_selenium = PythonOperator(task_id="dynamic_content", python_callable=get_pages_selenium, retries=1, dag=dag)
# extract information from the saved pages
extract_info = PythonOperator(task_id="extracting_info", python_callable=extract_information, retries=1, dag=dag)
# proscess information from the pages
proscess_info = PythonOperator(task_id="proscessing_info", python_callable=proscessing_information, retries=1, dag=dag)
# checking articles for missing links
check_for_missing_links = PythonOperator(task_id="checking_for_missing_links", python_callable=checking_for_links, retries=1, dag=dag)
# 
make_excel_file = PythonOperator(task_id="making_excel", python_callable=making_excel_file, retries=1, dag=dag)

# ======================================================================================================== 
# ORDER OF OPERATIONS
# ======================================================================================================== 
[get_pages_request, get_pages_selenium] >> extract_info >> proscess_info >> check_for_missing_links >> make_excel_file
