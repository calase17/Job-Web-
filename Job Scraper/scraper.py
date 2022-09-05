from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import fpdf
import pyshorteners
from pathlib import Path
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options

Path = "C:\Program Files\chromedriver.exe"

options = Options()
JOB_LIST = []
options.add_argument("--headless")
options.add_argument("--incognito")
driver = webdriver.Chrome(Path, options=options)

class Job:
    def __init__(self, title, location, company, salary, link):
        self.title = title
        self.location = location
        self.company = company
        self.salary = salary
        self.link = link

def preferences():
    print()
    print()
    print("Choose job search criteria")
    url = "https://www.indeed.co.uk/jobs?q=admin&l="
    while True: 
        try:
            no_of_pages = int(input("Enter how many pages you want searched through: "))
            lc = str(input("Enter Location: "))
            jt = int(input("Choose job type:\n 1: Permanent \n 2: Temporary\n"))
            if no_of_pages > 0 and lc != "" and (jt == 1) or (jt ==2):
                if jt == 1:
                    url = url+lc + "&radius=10&jt=permanent"
                else:
                     url = url+lc + "&radius=10&jt=temporary" 
                break
        except Exception as e:
            print(e)
            print("Enter Number please")
    return no_of_pages, url


def get_results():
    pages, main_url = preferences()
    print("Retreiving job search results... ")
    driver.get(main_url) 
    current_page = 1
    no_of_jobs = driver.find_element_by_id("searchCountPages")
    no_of_jobs = no_of_jobs.text
    no_of_jobs_list = no_of_jobs.split(" ")
    no_of_jobs = no_of_jobs_list[3]
    while current_page <= pages:
        if current_page > 1:
            page_key = str(current_page-1) +"0"
            driver.get(main_url+"&start="+page_key)
        main = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "resultsCol")))
        jobs = main.find_elements_by_css_selector(".jobsearch-SerpJobCard.unifiedRow.row.result.clickcard")
        for job in jobs:
            title1 = job.find_element_by_tag_name("h2")
            title1 = title1.text
            if len(title1) == 0:
                driver.get(main_url+"&start="+page_key)
                main = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "resultsCol")))
                jobs = main.find_elements_by_css_selector(".jobsearch-SerpJobCard.unifiedRow.row.result.clickcard")
                break
        for job in jobs:
            try:
                title = job.find_element_by_tag_name("h2")
                link = title.find_element_by_tag_name("a")
                url = link.get_attribute("href")
                tiny_url = pyshorteners.Shortener()
                shorted_url = tiny_url.tinyurl.short(url)
                title = title.text
                if "\n" in title:
                    title = title.replace("\n"," ")
                if title.endswith("new"):
                    title = re.sub("new", "", title)
                co = job.find_element_by_css_selector(".company")
                company = co.text
                locale = job.find_element_by_css_selector(".location.accessible-contrast-color-location")
                location = locale.text
                try:
                    bread = job.find_element_by_css_selector(".salaryText")
                    salary  = bread.text
                except Exception as f:
                    salary = "n/a"
                obj_job = Job(title, location, company, salary, shorted_url)
                JOB_LIST.append(obj_job)
            except Exception as e:
                print(e)
        current_page += 1
    return no_of_jobs
no_of_jobs = get_results()


def write_to_file(no_of_jobs):
    with open('JobSearchResults.txt', 'w') as f:
        f.write(no_of_jobs +" jobs have been retrieved\n\n")
        for j in JOB_LIST:
            f.write("Job Title: " +j.title +"\n")
            f.write("Location: " +j.location+"\n")
            f.write("Company: " +j.company+"\n")
            f.write("Salary: " + j.salary+"\n")
            f.write("Link for Job: "+ j.link+"\n")
            f.write("\n\n")

write_to_file(no_of_jobs)


pdf = fpdf.FPDF(format='A4')
pdf.set_margins(10.0,10.0,10.0)
pdf.add_page()
pdf.set_font("Arial", size=12)

with open('JobSearchResults.txt', 'r') as f:
    for line in f:
        line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(100,10,line,ln=1, align='')
    pdf.output("test.pdf")
    print("Jobs have been retrieved and added to pdf file: ")
     

driver.quit()

