from urllib import request
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import csv

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

import re
from selenium.common.exceptions import NoSuchElementException
#from scraperGoogle import webdriver
import bs4

class CompanyWorkflow():
    
    def __init__(self, browser, users_information):
        #self.list_of_links = list_of_links
        self.browser = browser
        self.company_job_title = None
        self.company_name = None
        self.company_job_location = None
        self.company_open_positions_url = []
        #This and apply can be temporary/method variables
        #self.a_fragment_identifier = None
        self.company_job_department = None
        self.job_id_number = None
        
        self.app_comp = None
        
        self.users_information = users_information
        self.application_company_name = None
        self.company_open_positions_link = None
        self.avoid_these_job_titles = ["senior", "sr", "principal"]
        self.soup = None
        self.company_open_positions_a = None    #For selenium to click
        self.application_company_name = None
        self.jobs_applied_to = {}
    
    #! Run determine_current_page and .header ONCE!!!!
    #! Once you get the list for all the open positions...
    #! Run a loop here .job_description => .should_apply() => .apply(.get_form_input_details(), .insert_resume(), .fill_in_form(), captcha_bullcrap()) 
    #!                                                  ^.get_job_data()
    #NOTE: For the 1st iteration let .determine_current_page() do all the work
    def company_workflow(self, job_link):
        #ALSO use this to get NEW... input Headers and their anwsers!!!!!! 
        #self.lets_run_some_tests()


        if "jobs.lever.co" in job_link:
            self.application_company_name = "lever"
            self.determine_current_page(job_link, self.application_company_name)
            self.company_job_openings(soup)
            
            for job_opening in self.company_job_openings:
                soup = self.apply_beautifulsoup(job_opening, "html")
                webpage_body = soup.find('body')
                if self.should_user_apply(webpage_body) == True:
                    self.lever_io_dat(job_opening, webpage_body)
                    soup = self.apply_beautifulsoup(job_link, "lxml")
                    self.get_form_input_details()
                    self.insert_resume()
                    self.fill_out_application()
                    self.keep_jobs_applied_to_info(job_link)
                self.reset_job_variables()
            
        elif "boards.greenhouse.io" in job_link:
            self.application_company_name = "greenhouse"
            self.determine_current_page(job_link, self.application_company_name)
            
            
            #self.link_to_other_company_openings(soup, application_company_name)
            apply_to_job, applic = self.convert_to_bs(job_link, soup, self.application_company_name)
            if apply_to_job:
                self.fill_out_application(applic, soup)
                #self.other_job_openings(self.link_to_other_jobs)
            #applic = self.greenhouse_io_start_page_decider(soup)
            applic = soup.find('div', id="application")
            self.find_and_organize_inputs(applic)
        #! div_main ==> lever.co = job_description

        
    
    def apply_beautifulsoup(self, job_link, parser):
        #the way I learned how to do it
        if parser == "lxml":
            result = requests.get(job_link)
            content = result.text
            soup = BeautifulSoup(content, 'lxml')
        #used for form_input_details()
        if parser == "html":
            page = requests.get(job_link)
            result = page.content
            soup = BeautifulSoup(result, 'html.parser')           
        return soup
    
        
    #TODO: This goes to all the links!!
    # def troubleshoot_xpath(self):
    #     for link in self.list_of_links:
    #         try:
    #             self.browser.get(link)
    #             time.sleep(2)
    #             job_title = self.browser.title
    #             print(f"Scraping job: {job_title}")

    #             # Search for the Google search name in the page
    #             google_search_name = job_title.split("-")[0].strip()
    #             print(f"Searching for: {google_search_name}")
    #             selenium_google_link = self.browser.find_element(By.XPATH, f'//ancestor::a/h3[not(descendant::br)][text()="{google_search_name}"]')
    #             print("Found search result")

    #             # Click on the Google search result link
    #             selenium_google_link.click()
    #             print("Clicked on the search result link")

    #             # Wait for the page to load and switch to the new tab
    #             WebDriverWait(self.browser, 10).until(EC.number_of_windows_to_be(2))
    #             self.browser.switch_to.window(self.browser.window_handles[-1])
    #             print("Switched to new tab")

    #             # Perform actions on the job page
    #             self.scrape_job_page()

    #             # Close the new tab and switch back to the search results tab
    #             self.browser.close()
    #             self.browser.switch_to.window(self.browser.window_handles[0])
    #             print("Closed new tab and switched back to search results tab")

    #         except NoSuchElementException:
    #             print(f"No search result found for: {google_search_name}")
    #             continue
    
    def lets_run_some_tests(self):
        print('Coolio, waiting...')
        time.sleep(5)
        print("Eff that old website! Let's test new one heard J.Cole said he heard Jonah Hill said it was tight! Out with the old in with the new!!")
        url = "https://boards.greenhouse.io/doubleverify/jobs/6622484002"
        self.browser.get(url)
        time.sleep(4)
        #Run any tests you want here!
        form_input_details = self.get_form_input_details(url)
        self.print_form_details(form_input_details)
        time.sleep(20)
        url="https://jobs.lever.co/govini/cc5f740a-7248-4246-8b77-e28ed27dd46d/apply"
        self.browser.get(url)
        time.sleep(4)
        #Run any tests you want here!
        form_input_details = self.get_form_input_details(url)
        self.print_form_details(form_input_details)
        time.sleep(20)
        
        print("You've done it all your hard work is done! Definitely wasn't worth it but whatever. Never doin that crap again.")
        time.sleep(5)
        return
        
    def delete_maybe(self, job_link):
        application_company_name = None
        
        
        
        #ALSO use this to get NEW... input Headers and their anwsers!!!!!! 
        self.lets_run_some_tests()


        
        if "jobs.lever.co" in job_link:
            application_company_name = "lever"
            self.app_comp = application_company_name
            
            #self.link_to_other_company_openings(soup, application_company_name)
            apply_to_job, applic = self.convert_to_bs(job_link, soup, application_company_name)
            if apply_to_job:
                self.fill_out_application(applic)
            self.lever_io_data(job_link, soup)
            self.find_and_organize_inputs(applic, soup)
            
        elif "boards.greenhouse.io" in job_link:
            application_company_name = "greenhouse"
            self.app_comp = application_company_name
            
            #self.link_to_other_company_openings(soup, application_company_name)
            apply_to_job, applic = self.convert_to_bs(job_link, soup, application_company_name)
            if apply_to_job:
                self.fill_out_application(applic, soup)
                #self.other_job_openings(self.link_to_other_jobs)
            #applic = self.greenhouse_io_start_page_decider(soup)
            applic = soup.find('div', id="application")
            self.find_and_organize_inputs(applic)
        #! div_main ==> lever.co = job_description
 
 
    def determine_current_page(self, job_link, application_company_name):
        soup = self.apply_beautifulsoup(job_link, "lxml")
        
        if application_company_name == "lever":
            webpage_body = soup.find('body')

            opening_link_application = soup.find('div', {"class": 'application-page'})
            opening_link_description = soup.find('div', {"class": 'posting-page'})
            opening_link_company_jobs = soup.find('div', {"class": "list-page"})

            if opening_link_application:
                try:
                    #TODO: This is v what we want to avoid!!!
                    company_open_positions = soup.find('a', {"class": "main-header-logo"})
                    application_webpage_html = soup.find("div", {"class": "application-page"})
                    
                    self.lever_co_header(webpage_body, soup)

                    self.company_open_positions_a.click()
                    return
                except:
                    #TODO: Change this Error type!
                    raise ConnectionError("ERROR: Companies other open positions are not present")
                
            elif opening_link_description:
                try:
                    a_tag_butt = soup.find('a', {'data-qa': 'btn-apply-bottom'})
                    div_tag_butt = soup.find('div', {'data-qa': 'btn-apply-bottom'})
                    application_at_bottom = soup.find("div", id="application")
                    print("Application at bottom or <button>")
                    if a_tag_butt:
                        #print("== Application at bottom of page")
                        print("== Press button to go to application")
                        has_apply_button = a_tag_butt
                        apply_to_job = self.should_user_apply(opening_link_description)
                    elif div_tag_butt:
                        print("== Press button to go to application")
                        has_apply_button = div_tag_butt
                        apply_to_job = self.should_user_apply(opening_link_description)    #apply_to_job = boolean | T=.click() && F=.lever_header() -> .company_job_openings()
                    if apply_to_job == True:
                        self.insert_resume()
                        self.find_and_organize_inputs(application_at_bottom)
                    elif not apply_to_job:
                        #TODO:
                        self.company_other_openings_href.click()
                        self.company_job_openings(soup, div_main, application_company_name)
                except:
                    raise "Something went wrong with the the greenhouse.io job_description page"
            elif opening_link_company_jobs:
                #TODO: parse through other_company_jobs for "lever"
                self.company_job_openings(soup, None, application_company_name)
            application = opening_link_application
                
        elif application_company_name == "greenhouse":
            div_main = soup.find("div", id="main")
            #I did it this way because it checks very few elements since 1 of these options are normally literally the next element
            next_elem = div_main.find_next()
            while next_elem:    #NOTE: REMEBER THIS DOESN'T INCREMENT next_elem SO IT'S THE SAME VALUE AS ABOVE!!!!
                if next_elem.name == "div" and (next_elem.get("id") == "flash-wrapper" or next_elem.get("id") == "flash_wrapper"):
                    print('-Job Page')
                    #return soup.find("div", id="flash-wrapper")
                    #break
                    flash_wrapper = soup.find("div", id=["flash-wrapper", "flash_wrapper"])
                    #Ex)https://boards.greenhouse.io/luminar
                    print("******* Flash_Wrapper = ")
                    print(flash_wrapper)
                    print("*******")
                    self.company_job_openings(soup, div_main, application_company_name)
                    return
                elif (next_elem.name == "div" and next_elem.get("id") == "embedded_job_board_wrapper"):
                    print('-Job Listings Page')
                    #return soup.find("div", id="embedded_job_board_wrapper")
                    embedded_job_board = soup.find("div", id="embedded_job_board_wrapper")
                    self.company_job_openings(soup, div_main, application_company_name)
                    return
                elif (next_elem.name == "section" and next_elem.get("class") == "level-0"):
                    print("-Company Job Openings Page")
                    print("A while loop for this is perfect for this because there can be multiple <section class='level-0'>")
                    #TODO: for this one in the elif you have to look through all "level-0" sections!!
                    self.company_job_openings(soup, div_main, application_company_name)
                    return soup.find("section", {"class": "level-0"})
                elif next_elem.name == "div" and next_elem.get("id") in ["app-body", "app_body"]:
                    app_body = next_elem
                    header = next_elem.find("div", id="header")
                    content = next_elem.find("div", id="content")
                    application = soup.find("div", id="application")
                    if header and content:
                        print("Job Description Page")
                        #self.link_to_other_company_openings(soup, application_company_name)
                        #self.company_job_openings(self, soup, div_main, application_company_name)
                        self.greenhouse_io_header(app_body, header, content)    #TODO: return *job_title, company, location, ???*
                    #else:
                        print("Application at bottom or <button>")
                        apply_button = div_main.find("button", text="Apply Here")
                        #TODO
 #! ^ MOVE UP 198 ^ ^ ^ ^ ^ ^ ^                       apply_button = div_main.find("button", text=["Apply Here", "Apply Now"])  #NOTE: !!!!! Maybe greenhouse doesn't have <button> ...    maybe it only has <a class="button">!?!?!?
                        #application_below_description = div_main.find("div", id="application")
                        #NOTE: I don't think greenhouse.io house <... target="_blank">
                        if apply_button:
                            print("== Press button to go to application")
                            apply_button.click()
                            time.sleep(5)
                            #self.greenhouse_io_application(application)
                            print("Application = ", end="")
                            print(application)
                            apply_to_job = self.should_user_apply(application)
                            #return application
                        elif application:
                            #self.should_user_apply(application)
                            print("== Application at bottom of page")
                            
                            apply_to_job = self.should_user_apply(content)
                        else:
                            print("Hmmm that's weird ? it's neither button nor application")
                            
                        if apply_to_job == True:
                            self.fill_out_application(application, soup)
                            #self.insert_resume(application)
                            #self.find_and_organize_inputs(application) #! <-- Change application to application_form!!!!
                        elif apply_to_job == False:
                            self.a_href.click()
                            time.sleep(4)
                            self.company_job_openings(soup, div_main, application_company_name)
                            return
                    break
                else:
                    next_elem = next_elem.find_next()
            self.company_other_openings_href.click()
            time.sleep(7)
            return apply_to_job, application
            #return
    
    #everything_about_job = app_body.get_text()
    #should_user_apply(everything_about_job)
    #greenhouse(job_description) => app_body
    def should_user_apply(self, job_description):
        #FILTER: keywords (industry experience//////)
        everything_about_job = job_description.get_text()

        #print(everything_about_job)
        experience_needed = r"\b\d+\s*(year|yr)s?\s+of\s+experience\b"
        #experience_needed = "You must be a diety; being a demigod or demigoddess is literally embarrassing... just go back to coloring if this is you. Literally useless & pathetic ewww"
        if re.search(experience_needed, everything_about_job):
            print("Experience requirement found!")
            print(re.search(experience_needed, everything_about_job))
            return False
        else:
            print("No experience requirement found!")
            print(re.search(experience_needed, everything_about_job))
            return True
    
    def company_job_openings(self, soup, div_main, application_company_name):
        #greenhouse.io == <div id="main">   =>   lever.co == ??? [?postings-wrapper?] -> maybe 'filter-bar'
        #greenhouse.io == <section class="level-0">   =>   lever.co == <div class="postings-group">
        #greenhouse.io == <section class="level-1">   =>   lever.co == <div class="posting">
        print("Application Company = " + application_company_name)
        
        
        if application_company_name == 'lever':
            #just getting a better(more narrowed result) filter
            postings_wrapper = soup.find('div', class_="postings-wrapper")
            current_url = self.browser.current_url
            perfect_url = self.try_adjusting_job_link(current_url)
            postings_group_apply = postings_wrapper.find_all('div', class_=lambda x: x and ('postings-group' in x or 'posting-apply' in x))
            
            
            #department_name_empty = True
            for section in postings_group_apply:
                print(section)
                company_department = section.find('div', class_='large-category-header').text
                #if company_department and department_name_empty:
                if company_department:
                    print(company_department)
                    #department_name_empty = False
                
                # if section.name == 'h3':
                #     company_department = section.text
                # if section.name == 'h4':
                #     print('This is most likely just a SUB-category so not really important otber than making sure we go through EVERY job it contains!')
                    
                #job_opening = section.find('div', {'class': 'opening'})
                if section.name == 'div' and section.get('class') == 'posting-apply':
                    job_opening_href = section.next_sibling
                    if job_opening_href.name == 'a' and job_opening_href.get('class') == 'posting-title':
                        button_to_job_description = job_opening_href
                        job_link = job_opening_href.get('href')
                        job_title = job_opening_href.find('h5').text
                        for bad_word in self.avoid_these_job_titles:
                            if bad_word not in job_title:
                                job_href = job_opening_href.get('href')
                                job_url = perfect_url + job_href
                                self.company_open_positions_url.append(job_url)
                                print(job_title)
                        span_tag = job_opening_href.find('span', {'class', 'sort-by-location'})
                        span_tag_company_team = job_opening_href.find('span', {'class': 'sort-by-team'})
                        span_tag_workplaceTypes = job_opening_href.find('span', {'class': 'workplaceTypes'})
                        if span_tag:
                            job_opening_location = span_tag.text
                        #job_opening_href.click()
            self.print_company_job_openings("company_job_openings", application_company_name, JobTitle=job_title, JobLocation=job_opening_location, WorkPlaceTypes=span_tag_workplaceTypes, CompanyDepartment=company_department, JobTeamInCompany=span_tag_company_team, JobHREF=job_link, ButtonToJob=button_to_job_description)
            return
        
        elif application_company_name == 'greenhouse':
            current_url = self.browser.current_url
            perfect_url = self.try_adjusting_job_link(current_url)
            sections = div_main.find_all('section', class_=lambda x: x and 'level' in x)
            #print(sections) #TODO: Make sure this list includes all 'level-0' and 'level-1' THEN the for loop below should parse through both 'levels'!!
            count = 0
            for section in sections:
                count += 1
                #if section.name == "class" and section.get("class") == 'level-0':
                if section.name == 'h3':
                    company_department = section.text
                    print(company_department)
                if section.name == 'h4':
                    print('This is most likely just a SUB-category so not really important other than making sure we go through EVERY job it contains!')
                    
                job_opening = section.find('div', {'class': 'opening'})
                if job_opening:
                    job_opening_href = job_opening.find('a')
                    if job_opening_href:
                        job_title = job_opening_href.text
                        print(job_title)
                        for bad_word in self.avoid_these_job_titles:
                            if bad_word not in job_title:
                                job_href = job_opening_href.get('href')
                                job_url = perfect_url + job_href
                                self.company_open_positions_url.append(job_url)
                        span_tag = job_opening.find('span', {'class', 'location'})
                        if span_tag:
                            job_opening_location = span_tag.text
                            print(job_opening_location)
                        #job_opening_href.click()
                if count == 20:
                    break
                print("-------")
            self.print_company_job_openings("company_job_openings", application_company_name, JobTitle=job_title, JobLocation=job_opening_location, ButtonToJob=job_href)
        return
    
    def print_company_job_openings(*args, **kwargs):
        print('\n\n\n')
        print('----------------------------------------------------------------------------------------------------')
        method_name = None
        for arg in args:
            if arg == 'greenhouse':
                print(method_name)
                print(arg)
                for key, value in kwargs.items():
                    print(key + ": " + str(value))
            elif arg == 'lever':
                print(method_name)
                print(arg)
                for key, value in kwargs.items():
                    print(key + ": " + str(value))
            else:
                method_name = arg
        print('----------------------------------------------------------------------------------------------------')
        print('\n\n\n')
    
    #The purpose of this method is pretty much only finding and retrieving the companies other open positions url!!!
    def lever_co_header(self, webpage_body):
        links_in_header = []
        print("\nThese are the links/elements that lead to this companies other available Job Openings:")
        current_url = self.browser.current_url
        print("Current URL: " + current_url)
        links_in_header.append(current_url)
        webpage_header = webpage_body.find('div', {"class": 'main-header-content'})
        self.company_open_positions_a = webpage_header.find('a', {"class": "main-header-logo"})
        print("Selenium Click => Companies other Job Openings: " + self.company_open_positions_a)
        #links_in_header.append(self.company_open_positions_a)
        try:
            if self.company_open_positions_a['href']:
                company_open_positions_href = self.company_open_positions_a['href']
                print("Webpage's Header link: " + company_open_positions_href)
                company_open_positions_url = company_open_positions_href
                links_in_header.append(company_open_positions_url)
        except:
            print("This company's webpage is dumb anyways! Trust me they would've probably overworked you anyways.")
        self.check_header_links(links_in_header)
        return
    
    def check_header_links(self, links_in_header):
        #! CANT SET VALUES TO LOCAL VARIABLES  REMEMBER!!!!!...  except for booleans I guess?
        first_link = True
        list_of_other_jobs_keyword
        for header_link in links_in_header:
            if first_link == True and "lever" == self.application_company_name:
                self.try_adjusting_job_link(header_link)
                list_of_other_jobs_keyword = 'list-page'
                first_link = False
            elif first_link == True and "greenhouse" in self.application_company_name:
                
                list_of_other_jobs_keywords = ''
                first_link == False
            self.browser.execute_script("window.open('{}', '_blank');".format(header_link))
            for handle in self.browser.window_handles:
                self.browser.switch_to.window(handle)
                if list_of_other_jobs_keyword in self.browser.page_source:
                    self.company_open_positions_link = header_link
                    return
        print("Hmmmm this is unexpected. I must be dumb...")
        if (self.company_open_positions_link == None):
            self.company_open_positions_a.click()
            time.sleep(5)
    
    def try_adjusting_job_link(self, job_link):
        if self.application_company_name == 'lever':
            adjusting_link = job_link.find('jobs.lever.co/') + len('jobs.lever.co/')
            still_adjusting = job_link.find('/', adjusting_link) + 1
            link_adjusted = job_link[:still_adjusting]
            print(link_adjusted)
            job_link = link_adjusted
            print(job_link)
        if self.application_company_name == 'greenhouse':
            adjusting_link = job_link.find('greenhouse.io/') + len('greenhouse.io/')
            still_adjusting = job_link.find('/', adjusting_link) + 1
            link_adjusted = job_link[:still_adjusting]
            print(link_adjusted)
            job_link = link_adjusted
            print(job_link)
        time.sleep(8)
        return job_link
    
    #line 570 #elif child.name == "a"
    #if ("button" in child.get("class")) => remember !BUTTON! to click
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!!!!!!!!!!!!!!!!!         greenhouse_io_BANNER  [not header]           !!!!!!!!!!!!!!!!!
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def greenhouse_io_header(self, app_body, header, content): #! ^ ^ ^ ^
        first_child = True
        searched_all_a = False
        string_tab = '\n'
        for child in header.children:
            if first_child:                 #! if child == '\n'     CHECK ||||||||||
                first_child = False
                continue
            elif child == string_tab:
                continue
            if child.name == "h1" and "app-title" in child.get("class"):
                self.company_job_title = child.get_text().strip()
            elif child.name == "span" and  "company-name" in child.get("class"):
                self.company_name = child.get_text().strip()    #"at Braintrust" => maybe look for 1st capital letter
            elif child.name == "a" and not searched_all_a:  #TODO: v only captured the 1st <a>
                # has_hash = header.find_all('a', href=(lambda value: value and '#' in value))
                # for a_tag in has_hash:
                #     if '/' in a_tag['href']:
                #         self.a_href = a_tag
                #     #! HTML <a href='#ANYTHINGH'> -> REMEMBER *#* means redirect to that part of the webpage
                #     elif '#' in a_tag['href']:
                #         self.a_fragment_identifier = a_tag
                # if self.company_other_openings_href == None:
                #     logo_container = app_body.find('div', class_="logo-container")
                #     company_openings_a = logo_container.find('a')
                #     self.company_other_openings_href = company_openings_a['href']
                # searched_all_a = True
                header_a_tags = header.find_all('a')
                for head_a_tag in header_a_tags:
                    if '/' in head_a_tag['href']:
                        self.company_other_openings_href = head_a_tag
                    elif '#' in head_a_tag['href']:
                        self.a_fragment_identifier = head_a_tag
                    elif head_a_tag == None:
                        logo_container = app_body.find('div', class_="logo-container")
                        company_openings_a = logo_container.find('a')
                        self.company_other_openings_href = company_openings_a['href']
                        searched_all_a = True
                #all_jobs_available_a_href = child['href']  #! ^ ^ ^ ^ ^ ^ ^ ^ ^
                #print("all_jobs_available_a_href 1 = ")
                #print(all_jobs_available_a_href)
                #! If it opens on job_description see the bottom is 'apply_button' or 'job_application'
                # print("all_jobs_available_a_href 2 = ")
                # all_jobs_available_a_href = child.decode_contents()
                #print(all_jobs_available_a_href)
                #!since child is the <a> remember to click it!!!
                #companies_jobs_link_a = child
            elif child.name == "div" and "location" in child.get("class"):
                self.company_job_location = child.get_text().strip()
            else:
                print("child = ")
                print(child)
            #self.company_openings_test_link = 
        if self.company_other_openings_href == None:
            self.print_company_job_openings("greenhous_io_header()", "greenhouse", JobTitle=self.company_job_title, CompayName=self.company_name, JobLocation=self.company_job_location, JobHREF="Couldnt Find", LinkToApplicationOnPageID=self.a_fragment_identifier)
        else:
            self.print_company_job_openings("greenhous_io_header()", "greenhouse", JobTitle=self.company_job_title, CompayName=self.company_name, JobLocation=self.company_job_location, JobHREF=self.company_other_openings_href, LinkToApplicationOnPageID=self.a_fragment_identifier)
        return
        #self.greenhouse_io_content(app_body, content)
        # if self.a_fragment_identifier == None:
        #     return self.company_job_title, self.company_name, self.company_job_location, self.company_other_openings_href
        # else:
        #     return self.company_job_title, self.company_name, self.company_job_location, self.company_other_openings_href, self.a_fragment_identifier
    
    
            #         position_title = soup.find('h2')
            #         job_title = position_title.get_text().split()
            #         job_info = soup.find('div', {"class": "posting-categories"})
            #         job_location = job_info.find('div', {"class": 'location'}).get_text().strip()
            #         job_department = job_info.find('div', {"class": 'department'}).get_text().strip()
            #         job_commitment = job_info.find('div', {"class": 'commitment'}).get_text().strip()
            #         job_style = job_info.find('div', {"class": 'workplaceTypes'}).get_text().strip()
            #         print("HERE------------------------------------")
                    
            #         a_tag_butt = soup.find('a', {'data-qa': 'btn-apply-bottom'})
            #         div_tag_butt = soup.find('div', {'data-qa': 'btn-apply-bottom'})
            #         job_apply_butt = None
            #         link_to_apply = None
            #         #job_apply_butt = soup.select_one('a.btn-apply-bottom, div.btn-apply-bottom')
            #         #if job_apply_butt.name == 'div':
            #         if div_tag_butt:
            #             job_apply_butt = job_apply_butt.find('a')
            #             link_to_apply = job_apply_butt['href']
            #         elif a_tag_butt:
            #             link_to__apply = a_tag_butt['href']
            #     except:
            #         #TODO: Change this Error type!
            #         raise ConnectionError("ERROR: Companies other open positions are not present")
            # return
    

    

    

    





    

    
    #filter out already applied jobs
    #traverse job webpage
    #?????
    def lever_io_dat(self, joby_link, soup):
        self.joby_link = joby_link
        print("===Ballsack = inside the lever.co")
        #opening_link_application = soup.find('div', class_='page-application')      #application immediate
        opening_link_application = soup.find('div', {"class": 'application-page'})
        #opening_link_description = soup.find('div', class_='page-show')             #regular description start
        opening_link_description = soup.find('div', {"class": 'posting-page'})          #NOTE: In HTML class='one two' needs 2 class calls I think!?!?!?
        print("===Ballsack = opening_link_application = ", end="")
        #print(opening_link_application)
        print("You are on the Job Application webpage")
        print("===Ballsack = opening_link_description = ", end="")
        #print(opening_link_description)
        print("You are on the Job Description webpage")
        try:
            other_company_jobs = soup.find('div', {"class": 'page show'})
            company_open_positions = other_company_jobs.find('a', {"class": "main-header-logo"})
            if company_open_positions['href']:
                plethora_of_jobs = company_open_positions['href']
                print(plethora_of_jobs)
        except:
            print("Couldn't find the logo with the lick to plethora_of_jobs")
        
        #if soup.find('a', class_='main-header-logo'):
        if opening_link_application:
            try:
                company_open_positions = soup.find('a', {"class": "main-header-logo"})
                #company_open_positions = soup.find('a', class_=['main-header-logo', 'main-header'])
                plethora_of_jobs = company_open_positions['href']
                print("===Ballsack = plethora_of_jobs = ", end="")
                print(plethora_of_jobs)
                application_webpage_html = soup.find("div", {"class": "application-page"})
                self.lever_io_application(joby_link, application_webpage_html)
                #return opening_link_application
            except:
                #TODO: Change this Error type!
                raise ConnectionError("ERROR: Companies other open positions are not present")
        elif opening_link_description:
            print("===Ballsack = lever.co is working")
            try:
                print("===Ballsack = inside the try lever.co")
                position_title = soup.find('h2')
                job_title = position_title.get_text().split()
                print("===Ballsack = job_title = ", end="")
                #print(job_title.get_text())
                print(job_title)
                #? .position_title.find() doesn't work b/c the <h2> and <div> are siblings!!
                # job_info = position_title.find('div', {"class": "posting-categories"})
                job_info = soup.find('div', {"class": "posting-categories"})
                job_location = job_info.find('div', {"class": 'location'}).get_text().strip()
                job_department = job_info.find('div', {"class": 'department'}).get_text().strip()
                job_commitment = job_info.find('div', {"class": 'commitment'}).get_text().strip()
                job_style = job_info.find('div', {"class": 'workplaceTypes'}).get_text().strip()
                print("HERE------------------------------------")
                print(job_location)
        
                a_tag_butt = soup.find('a', {'data-qa': 'btn-apply-bottom'})
                div_tag_butt = soup.find('div', {'data-qa': 'btn-apply-bottom'})
                job_apply_butt = None
                link_to_apply = None
                #job_apply_butt = soup.select_one('a.btn-apply-bottom, div.btn-apply-bottom')
                #if job_apply_butt.name == 'div':
                if div_tag_butt:
                    job_apply_butt = job_apply_butt.find('a')
                    link_to_apply = job_apply_butt['href']
                elif a_tag_butt:
                    link_to__apply = a_tag_butt['href']
                
                print("===Ballsack = link_to_apply = ", end="")
                print(link_to_apply)

            except:
                #TODO: Change this Error type!
                raise ConnectionError("ERROR: Companies other open positions are not present")
        #print("===Ballsack = leaving the lever.co")
        return soup

    #if id="app_body" and [check which page you are on]
    
    def greenhouse_io_start_page_decide(self, soup): #if (child of main is one of these)
        print("Welcome fair maiden this company has gathered to make decisions based on your skin color... please after you!")
        div_main = soup.find("div", id="main")
        next_elem = div_main.find_next()
        while next_elem:
            if next_elem.name == "div" and next_elem.get("id") == "flash-wrapper":
                print('-Job Page')
                return soup.find("div", id="flash-wrapper")
                break
            elif (next_elem.name == "div" and next_elem.get("id") == "embedded_job_board_wrapper"):
                print('-Job Listings Page')
                return soup.find("div", id="embedded_job_board_wrapper")
                break
            elif (next_elem.name == "section" and next_elem.get("class") == "level-0"):
                print("-Job Listings Page")
                print("A while loop for this is perfect for this because there can be multiple <section class='level-0'>")
                #TODO: for this one in the elif you have to look through all "level-0" sections!!
                return soup.find("section", {"class": "level-0"})
            elif next_elem.name == "div" and next_elem.get("id") in ["app-body", "app_body"]:
                app_body = next_elem
                header = next_elem.find("div", id="header")
                content = next_elem.find("div", id="content")
                application = soup.find("div", id="application")
                if header and content:
                    print("Job Description Page")
                    self.greenhouse_io_header(app_body, header, content)
                else:
                    print("Application at bottom or <button>")
                    #TODO
                    apply_button = div_main.find("button", text="Apply Here")
                    if application:
                        self.greenhouse_io_application(application)
                    elif apply_button:
                        apply_button.click()
                        time.sleep(5)
                        self.greenhouse_io_application(application)
                        print("Application = ", end="")
                        print(application)
                        return application
                break
            else:
                next_elem = next_elem.find_next()
        print("Guess the .greenhouse_io_start_page_detector() while loop doesn't work")

    #! FIND AND ATTACH RESUME 1st B/C AUTOFILL SUCKS
    def attach_resum(self, application):
        resume_element = application.find_element(By.XPATH, "//*[@id[contains(@id, 'resume')]]")
        resume_path = "get from .env file"
        
        #How does the form want us to upload our resume? Button click...
        while True:
            upload_by_button = application.find_element(By.TAG_NAME, "//fieldset[@aria-describedby='resume-allowable-file-types']")
            if upload_by_button:
                ActionChains(self.browser).move_to_element(upload_by_button).click().perform()
                upload_by_button.send_keys(resume_path)
                break
        try:
            ActionChains(self.browser).send_keys(Keys.ENTER).perform()
        except:
            raise "Something went wrong meanie! Help me :("





#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!       REMEMBER TO COUNT THE NUMBER OF OPEN SENIOR > ROLES AVAILABLE           !
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        #! FIND AND ATTACH RESUME 1st B/C AUTOFILL SUCKS
    def insert_resume(self):
        print(">>>>>>   .insert_resume()")
        resume_path = self.users_information.get('WORK_RESUME_PATH')
        print(resume_path)
        
        if self.app_comp == 'greenhouse':
            element = self.browser.find_element(By.XPATH, "//button[text()='Attach']")
            #element = self.browser.find_element(By.XPATH, "//button[contains(text, 'ATTACH')]")
            #element = self.browser.find_elements(By.ID, "application")
            print("0.1 = ", end="")
            print(element)
            if not element:
                element = self.browser.find_element(By.CLASS_NAME, "resume")
                print("0.2 = ", end="")
                print(element)
            if not element:
                element = self.browser.find_element(By.XPATH, "//button[text()='Attach']")
                print("0.3 = ", end="")
                print(element)
            if not element:
                print("That's some bull crap! Can't scroll")
            self.browser.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(2)
        print("1")
        
        #for *lever.co* I believe
        resume_file_input = self.browser.find_elements(By.XPATH, '//input[data-qa="input-resume"]')
        print("2")
        print(resume_file_input)
        print("2.1 = ", end="")
        if resume_file_input:
            print("3")
            resume_file_input[0].send_keys(resume_path)
            print("4")
        else:
            print("5")
            #resume_upload_button = self.browser.find_element(By.CSS_SELECTOR, 'button.visible-resume-upload')
            resume_upload_button = self.browser.find_element(By.CSS_SELECTOR, 'button[aria-describedby="resume-allowable-file-types"]')
            print("--------------------------------------------------------")
            print(resume_upload_button)
            print("--------------------------------------------------------")
            #print()
            print("6")
            if resume_upload_button:
                time.sleep(1)
                print("8")
                input_elements = self.get_input_tag_elements()
                
                #NOTE: [https://dev.to/razgandeanu/how-to-upload-files-with-selenium-3gj3]
                # input_element, is_visible = self.find_visible_input('input[data-qa="input-resume"]')
                input_element, is_visible = self.find_visible_input('input[type="file"]')
                print("Bargain-Mart")
                print((input_element, is_visible))
                
                
                upload_input = self.browser.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                upload_input.send_keys(resume_path)
                print("8.1")
                time.sleep(2)

                print("13")
            else:
                raise Exception('Could not find resume upload element')
        print("14 Holy Crap")
        return
    
    def get_labia(self, input_element):
        # Check for the special case: 'button' and 'submit application' in input_element
        input_element_str = str(input_element).lower()
        if 'button' in input_element_str and 'submit application' in input_element_str:
            return 'Submit Application'
        
        if input_element.get('type') == 'radio':
            label = self.print_parent_hierarchy(input_element)
            return label

        label = None

        # Case 1: Check if the label is a direct previous sibling of the input element
        label = input_element.find_previous_sibling('label')

        # Case 2: Check if the label is inside a parent container
        if not label:
            parent = input_element.find_parent()
            if parent:
                label = parent.find('label')

        # Case 3: Check if the label is associated using the "for" attribute
        if not label:
            input_id = input_element.get('id')
            if input_id:
                label = input_element.find_previous('label', attrs={'for': input_id})

        # Case 4: Check if the input element is a child of a label element
        if not label:
            parent_label = input_element.find_parent('label')
            if parent_label:
                label = parent_label

        # Case 5: Check if a label is inside a parent container of the input element
        if not label:
            parent = input_element.find_parent()
            if parent:
                label = parent.find('label')

        # Check if the label contains a nested div element with the class "application-label" (case for Input 18)
        if label:
            app_label = label.find(lambda tag: 'class' in tag.attrs and 'application-label' in tag['class'])
            if app_label:
                label = app_label

        if label:
            label_text = label.text.strip()

            # If the standard asterisk (*) or fullwidth asterisk (✱) is present, remove everything after it
            if '*' in label_text:
                label_text = label_text.split('*')[0].strip() + ' *'
            elif '✱' in label_text:
                label_text = label_text.split('✱')[0].strip() + ' ✱'
            else:
                # If the newline character (\n) is present, remove it and everything after it
                label_text = label_text.split('\n')[0].strip()

            return label_text

        # Case 6: Check if the input_element has a placeholder attribute
        placeholder = input_element.get('placeholder')
        if placeholder:
            return f"Placeholder ~ {placeholder}"

        return None
    
    def print_parent_hierarchy(self, element, stop_level=5):
        current_level = 0
        while (current_level <= stop_level):
            print(f"Level {current_level}:")
            if current_level == 0 or current_level == 5:
                if current_level == 0:
                    print(element.prettify())
                if current_level == 5:
                    sauce = element.next_element.get_text(strip=True)
                    print("EFF CHATGPT THAT THING IS GAY AND SUCKS BALLS: ", end='')
                    print(sauce)
                    return sauce
            element = element.parent
            current_level += 1

    #! Include checkboxes!!!!
    def get_form_input_details(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        form_fields = soup.find_all(['input', 'textarea', 'button', 'select'])

        form_input_details = []
        processed_radios = set()

        for i, field in enumerate(form_fields, start=1):
            input_type = field.get('type')
            input_id = field.get('id')
            input_label = ''
            is_hidden = field.get('style') == 'display: none;' or input_type == 'hidden'
            input_html = str(field).strip()

            if field.name == 'button':
                input_type = 'button'
                # Skip captcha buttons
                if 'h-captcha' in field.get('class', []) or 'g-recaptcha' in field.get('class', []):
                    continue
            elif field.name == 'textarea':
                input_type = 'textarea'
            elif field.name == 'select':
                input_type = 'select'

            # Add a check for the input types you want to keep
            if input_type not in ['text', 'email', 'password', 'select', 'radio', 'checkbox', 'textarea', 'button'] and input_id != 'education_school_name':
                continue

            values = []
            if input_type == 'select':
                options = field.find_all('option')
                for option in options:
                    values.append(option.text.strip())

            if input_type == 'radio':
                #print("Radio button in get_form_input_details:", field)  # Debugging line
                radio_name = field.get('name')
                if radio_name in processed_radios:
                    continue
                processed_radios.add(radio_name)
                radio_group = soup.find_all('input', {'name': radio_name})
                values = [radio.get('value') for radio in radio_group]
                input_html = ''.join([str(radio).strip() for radio in radio_group])
                
                #radio_button = soup.find('input', attrs={'name': 'eeo[race]', 'type': 'radio'})
                #self.print_parent_hierarchy(radio_button)
                
                # Call get_label for the entire radio button group
                input_label = self.get_labia(field)
            else:
                # Call get_label for other input types
                input_label = self.get_labia(field)

            # Skip hidden fields without a label
            if is_hidden and not input_label:
                continue

            is_dynamic = False
            related_elements = []

            # Check the field's ancestors for the 'data-show-if' attribute and 'display: none;' style
            current_element = field
            while current_element:
                if current_element.has_attr('data-show-if'):
                    is_dynamic = True
                    related_elements = [
                        {
                            'related_field_id': current_element['data-show-if'].split('==')[0],
                            'trigger_value': current_element['data-show-if'].split('==')[1],
                        }
                    ]
                if current_element.get('style', '') == 'display: none;':
                    is_hidden = True
                current_element = current_element.find_parent()

            form_input_details.append({
                'label': input_label,
                'type': input_type,
                'values': values,
                'is_hidden': is_hidden,
                'html': input_html,
                'dynamic': is_dynamic,
                'related_elements': related_elements,
            })

        return form_input_details
      
    def print_form_details(self, form_inputs):
        print('\n\n\n')
        jam = "10"
            
        if jam == "1":
            print('--------------------------------------------')
            print("Form Input Details: ", end="")
            for i, detail in enumerate(form_inputs, start=1):
                print(f"Input {i}:")
                print(f"  Label: {detail['label']}")
                print(f"  Type: {detail['type']}")
                print(f"  Values: {detail['values']}")
                print(f"  Is Hidden: {detail['is_hidden']}")
                print(f"  HTML: {detail['html']}")
            print('--------------------------------------------')
            print("\n")
            
        else:
            print('--------------------------------------------')
            print("Form Input Details: ", end="")
            for i, detail in enumerate(form_inputs, start=1):
                print(f"Input {i}:")
                print(f"  Label: {detail['label']}")
                print(f"  Type: {detail['type']}")
                print(f"  Values: {detail['values']}")
                print(f"  Is Hidden: {detail['is_hidden']}")
                print(f"  HTML: {detail['html']}")
                print(f"  Dynamic: {detail['dynamic']}")
                print(f"  Related Elements: {detail['related_elements']}")
            print('--------------------------------------------')
            print("\n")        
        

    
    
    
    
    
    
        
    def keep_jobs_applied_to_info(self, job_link):
        self.jobs_applied_to_info.append({
            'Job_URL': job_link,
            'Company_Name': self.company_name,
            'Job_Title': self.company_job_title,
            'Company_Job_Location': self.company_job_location,
            'Company_Department': self.company_job_department,
            'Job_ID_Number': self.job_id_number,
        })  
        

                
    def get_value_for_label(self, label):
        label_to_key_mapping = {
            'Full Name': 'FULL_NAME',
            # Add other custom mappings here
        }

        if label in label_to_key_mapping:
            key = label_to_key_mapping[label]
            if key == 'FULL_NAME':
                first_name = self.users_information.get('FIRST_NAME', '')
                middle_initial = self.users_information.get('MIDDLE_INITIAL', '')
                last_name = self.users_information.get('LAST_NAME', '')
                return f"{first_name} {middle_initial} {last_name}".strip()

        # If there's no custom mapping for the label, return the value associated with the label as the key
        return self.users_information.get(label, None)
        
        
        
        
        
    def fill_form_fields(self, form_input_details):
        # Start the Selenium browser
        browser = webdriver.Firefox()
        browser.get(self.url)

        for input_detail in form_input_details:
            env_key = self.get_env_key_for_label(input_detail['label'])
            env_value = self.users_information.get(env_key)

            if env_value is None:
                print(f"New question not found in the .env file: {input_detail['label']}")
                if input_detail['values']:
                    print("Possible answers:")
                    for value in input_detail['values']:
                        print(f" - {value}")
                env_value = input("Please enter your answer: ")
                # Save the new value to the .env file here, if needed

            if env_value is not None:
                # Fill in the form field based on its type
                if input_detail['type'] == 'textarea':
                    textarea = input_detail['html']
                    textarea_element = browser.find_element_by_name(textarea['name'])
                    textarea_element.send_keys(env_value)
                elif input_detail['type'] == 'select':
                    select = input_detail['html']
                    select_element = Select(browser.find_element_by_name(select['name']))
                    select_element.select_by_visible_text(env_value)
                elif input_detail['type'] == 'text':
                    text_element = browser.find_element_by_name(input_detail['html']['name'])
                    text_element.send_keys(env_value)
                elif input_detail['type'] == 'email':
                    email_element = browser.find_element_by_name(input_detail['html']['name'])
                    email_element.send_keys(env_value)
                elif input_detail['type'] == 'password':
                    password_element = browser.find_element_by_name(input_detail['html']['name'])
                    password_element.send_keys(env_value)
                elif input_detail['type'] == 'checkbox':
                    checkbox_element = browser.find_element_by_name(input_detail['html']['name'])
                    if env_value.lower() in ['true', 'yes']:
                        checkbox_element.click()
                elif input_detail['type'] == 'radio':
                    radio_elements = browser.find_elements_by_name(input_detail['html']['name'])
                    for radio_element in radio_elements:
                        if radio_element.get_attribute('value') == env_value:
                            radio_element.click()
                            break

        # Click the submit button
        submit_button = browser.find_element_by_css_selector("input[type='submit'], button[type='submit']")
        submit_button.click()
    
    
    
    
    
    
    
    
    
    def ninety_percent_correct(self, form_question):
        stripper_string = form_question.strip()
        total_value = len(stripper_string)
        add_percent = 1 / total_value
        percent_correct = 0
        for word in form_question:
            for key_value in self.env_key_values:
                stripper_env = self.env_key_values.strip()
                for env_words in stripper_env:
                    percent_correct += add_percent
        if (.9 <= (percent_correct/total_value)):
            return True
        return False
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
        
        
        
        
        
        
        
        
    #TODO: v turn all the calls to this application_process() 
    #def fill_out_application(self, applic, soup):
        self.insert_resume()
        form_data = self.find_and_organize_inputs(applic, soup)       

    def find_visible_input(self, selector):
        input_element = self.browser.find_element(By.CSS_SELECTOR, selector)
        is_hidden = input_element.get_attribute('type') == 'hidden' or not input_element.is_displayed()
        if is_hidden:
            self.browser.execute_script("arguments[0].style.display = 'block';", input_element)
            is_hidden = input_element.get_attribute('type') == 'hidden' or not input_element.is_displayed()
        return input_element, not is_hidden 
        
    def is_input_invisible(self, input_element):
        from scraperGoogle import webdriver
        """
        Checks if an input element is invisible to the user
        Returns True if the input is invisible, False otherwise
        """
        if input_element is None:
            return False
        
        # Check if input element itself is hidden
        if input_element.get_attribute("type") == "hidden" or input_element.get_attribute("style") == "display: none;":
            return True
        
        # Check if parent element is hidden
        print(input_element)
        print(type(input_element))
        parent_element = input_element.find_element(By.XPATH, '..')
        while parent_element is not None:
            if parent_element.get_attribute("style") == "display: none;":
                return True
            parent_element = parent_element.find_element(By.XPATH, '..')
        return False

    def get_form_input_details(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        input_elements = soup.find_all(['input', 'textarea', 'select'])

        input_details = []

        for i, input_element in enumerate(input_elements):
            details = {
                'Label': self.get_label(input_element),
                'Type': input_element.get('type'),
                'Values': [],
                'Is_Hidden': input_element.get('type') == 'hidden',
                'HTML': str(input_element)
            }
            if input_element.name == 'select':
                details['Values'] = [option.get_text(strip=True) for option in input_element.find_all('option')]
            input_details.append(details)

        return input_details






#! Important Notes

#app_body = soup.find("div", id=["app_body", "app-body"])   <---greenhouse.io









    
        
        









