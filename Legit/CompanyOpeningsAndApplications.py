#1)Put everything in the soup_elements necessary
#2)Go into all the methods and take out the call to smaller methods
#3)Fill them in accordingly



from urllib import request
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import csv

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

import re
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
#from scraperGoogle import webdriver
import bs4
from bs4 import Tag
from bs4.element import NavigableString
import spacy
from fuzzywuzzy import fuzz
# import Legit.config as config
# ^ handle_custom_rules()
import config

import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from transformers import GPTNeoForCausalLM, GPT2Tokenizer


#! Filter out string "professional experience is a must"


import torch


from urllib.parse import urljoin


class CompanyWorkflow():

    # def __init__(self, JobSearchWorkflow_instance, browser, users_information, init_users_job_search_requirements, jobs_applied_to_this_session, tokenizer, model, nlp, lemmatizer, custom_rules, q_and_a, custom_synonyms, senior_experience):
    def __init__(self, JobSearchWorkflow_instance, browser, users_information, init_users_job_search_requirements, jobs_applied_to_this_session, tokenizer, model, nlp, lemmatizer, custom_rules, q_and_a, custom_synonyms):
        if JobSearchWorkflow_instance is None:
            raise ValueError("JobSearchWorkflow_instance cannot be None")
        if browser is None:
            raise ValueError("browser cannot be None")
        
        
        #! *************************************************************************************
        # THESE VARIABLES NEED "NEW NAMES" FOOL: job_link_url, company_open_positions_url, company_open_positions_link!!!!!
        
        
        self.JobSearchWorkflow_instance = JobSearchWorkflow_instance
        self.browser = browser
        self.current_url = None


        self.list_of_links = []
        #This and apply can be temporary/method variables ???
        #! DEPRICATED DEPRICATED DEPRICATED DEPRICATED DEPRICATED
        #self.a_fragment_identifier = None
        

        
        #users .env values
        self.users_information = users_information  #{}
        self.init_users_job_search_requirements = init_users_job_search_requirements  #{}
        #the current company during this entire run
        self.application_company_name = None
        #URL to company's other job openings
        #self.companys_internal_job_openings_url = None
        # V V V V V V V V V V V V V V V V V V V V V V V
        self.companys_internal_job_openings_URL = None
        # v users_job_search_requirements["entry_level"]
        #self.senior_experience = senior_experience

        self.prior_experience_keywords = ["senior", "sr", "principal", "lead", "manager"]
        # v Replace this w/ dictionary variable and everytime a new webpage is loaded...  check the order of self.job_application_webpage(this will get all our soup stuff ready if need be) 
        #self.soup = None
        #TODO: v This can easily be done away with!!!
        #self.company_open_positions_a = None    #For selenium to click
        
        self.jobs_applied_to_this_session = jobs_applied_to_this_session  #{}
        #! DEPRICATED DEPRICATED DEPRICATED DEPRICATED DEPRICATED
        #self.company_other_openings_href = None
        

        #this is to ensure only 1 Resume/CV label is added to the form_input_details
        #!!!! GET RID OF THIS !!!! GET RID OF THIS !!!! GET RID OF THIS !!!! GET RID OF THIS !!!!
        self.one_resume_label = False
    
        self.form_input_details = {}
        self.form_input_extended = None
    
        
        #init_gpt_neo()
        self.tokenizer = tokenizer
        self.model = model
        #load_nlp()
        self.nlp = nlp
        #load_company_resources()
        self.lemmatizer = lemmatizer
        
        
        
        self.custom_rules = custom_rules
        self.q_and_a = q_and_a
        self.custom_synonyms = custom_synonyms
        
        
        self.env_path = '.env'
        self.sibling_company_job_links = None  #[]
                                                                                     # v greenhouse doesn't have
        self.job_application_webpage = ["Internal-Job-Listings", "Job-Description", "Job-Application", "Submitted-Application"]
                                         # ^ starts at 0
        
        
        self.soup_elements = {}

    
    def init_reset_webpage_soup_elements(self):
        self.soup_elements = {}
    
    def init_users_job_search_requirements(self):
        self.users_job_search_requirements = {
            "user_desired_job_title": [],
            "user_preferred_locations": [],
            "user_preferred_workplaceType": ["in-office", "hybrid", "remote"],
            "employment_type": [],  #Not really something I'm checking for
            "entry_level": True, 
        }
    
    def init_current_jobs_details(self):
        #temp_job_details
        self.current_jobs_details = {
            "job_url": None,
            "job_title": None,
            "job_location": None,
            "company_name": None,
            "job_workplaceType": None,
            "company_department": None,
            "job_id_number": None,
            "job_release_date": None,
            "employment_type": None,
            "experience_level": None,
            "years_of_experience": None,
            "company_industry": None,
            #"education_requirement": None,
            #"skills": None,
            #"security_clearance": None
        }
        
    '''
    def keep_jobs_applied_to_info(self, job_link):
        self.jobs_applied_to_this_session.append({
            'Job_URL': job_link,
            'Company_Name': self.company_name,
            'Job_Title': self.company_job_title,
            'Company_Job_Location': self.company_job_location,
            'Company_Department': self.company_job_department,
            'Job_ID_Number': self.job_id_number,
        })
    '''
    def keep_jobs_applied_to_info(self):
        self.jobs_applied_to_this_session.append(self.current_jobs_details)
    
    def reset_every_job_variable(self):
        self.init_current_jobs_details()
        self.init_reset_webpage_soup_elements()
        self.form_input_details = {}
        self.form_input_extended = None
#???????????????????????????????????????????????????????????????????????????????????????????????????????????????????

    #TODO:CHANGE METHOD -> return here everytime there is a change of webpages(URL)
        #TODO: so basically based/controlled by "self.job_application_webpage"
    #TODO:and then call "handle" methods to assist the main method call the necessary helper methods!! 
    #***
    def company_workflow(self, incoming_link):
        print("company_workflow()")

        if type(incoming_link) is list:
            print("Should be a list: incoming_link = ", incoming_link)
            self.current_url = incoming_link[0]
            self.sibling_company_job_links = incoming_link.copy()
        elif type(incoming_link) is str:
            print("Should be a string: incoming_link = ", incoming_link)
            self.current_url = incoming_link
        
        #TODO: Make sure this always sets incoming_link as the 1st index OTHERWISE for loop will fail
        self.list_of_links.append(self.current_url)

        if "jobs.lever.co" in self.current_url:
            self.application_company_name = "lever"
        elif "boards.greenhouse.io" in self.current_url:
            self.application_company_name = "greenhouse"
        #1.10) Links that are neither of these^ should get stopped here!
        else:
            print("Neither 'lever' nor 'greenhouse' ssooo...   idk")
                
        self.determine_current_page(self.current_url, self.application_company_name)
        #? If v this link isn't present for the 1st what makes the others different!?!?!?
        self.find_companys_internal_job_openings_URL()
        self.filter_companys_current_job_opening_urls()
        webpage_num = 0
        
        for job_opening in self.list_of_links:
            #TODO: Ensure -> self.current_url should always lag 1 behind EXCEPT FOR...  the 1st index!!??
                #Also, incase we get routed somewhere else!
            if self.current_url != job_opening:
                self.browser.get(job_opening)
            elif self.current_url == job_opening:
                print("BOOM skipped click from Google visit! Should only be for the 1st iteration...")
                pass
                
            try:    #what if the link is broken...   like old link b/c the job has been filled
                #Did it this way just to ensure all methods are on the same page
                self.current_url = self.browser.current_url
            except:
                continue
            
            if self.job_application_webpage[webpage_num] == "Internal-Job-Listings":
                webpage_num = self.collect_companies_current_job_openings()
            
            self.init_reset_webpage_soup_elements()
            if self.job_application_webpage[webpage_num] == "Job-Description":
                webpage_num = self.analyze_job_suitabililty()
            if self.job_application_webpage[webpage_num] == "Job-Application":
                webpage_num = self.apply_to_job()
            if self.job_application_webpage[webpage_num] == "Submitted-Application":
                
                self.reset_every_job_variable()
                webpage_num = 
            if:     #Nothing  MAYBE actually just an else
                self.reset_every_job_variable()
                webpage_num = 
        
        
        
        
        # #TODO - DRAFT 2
        # #TODO: This method returns things ssooo either fix what it returns or make this line = something
        # self.determine_current_page(self.current_url, self.application_company_name)
        
        
        # while len(self.list_of_links) != 0 and len(self.sibling_company_job_links) != 0:
        #     #1.20) So ALWAYS check banner 1st to get the url to internal jobs
        #     #and don't stop till it's found!!
        #     #TODO: Find out if this is necessary
        #     if self.companys_internal_job_openings_URL == None:
        #         #TODO: FIX / FINISH THIS!!
        #         self.find_companys_internal_job_openings_URL()
            
            
        #     self.determine_current_page(self.current_url, self.application_company_name)
            
        #     if self.job_application_webpage[0]:
        #         #Put here due to "greenhouse" but it's purpose is to hold job description!
        #         self.current_jobs_details["job_url"] = self.current_url
        #         self.analyze_job_suitabililty()
        #     elif self.job_application_webpage[1]:
        #             #stuff
        #     elif self.job_application_webpage[2]:
        #             #stuff
        #     elif self.job_application_webpage[3]:
        #             #stuff
        #     else
        #             #stuff
        
        
        
        
        
        # #TODO - DRAFT 1
        # #! RE-DISTRUBUTE THIS PROPERLY!!!!!!!
        # soup = self.apply_beautifulsoup(self.current_url, "lxml")
        # div_main = soup.find("div", id="main")
        # self.collect_companies_current_job_openings(soup, div_main)
        # self.filter_companys_current_job_opening_urls()
        
        # for job_opening in self.list_of_links:
        #     self.browser.get(job_opening)
        #     #self.current_url_url = self.browser.current_url   #Dumb -> it's redundant
        #     soup = self.apply_beautifulsoup(job_opening, "lxml")

        #     webpage_body = soup.find('body')
        #     if self.should_user_apply(webpage_body) == True:
        #         #TODO: greenhouse_io_data()???
        #         self.lever_io_data(job_opening, webpage_body)
        #         soup = self.apply_beautifulsoup(self.current_url, "html")
        #         form_input_details = self.get_form_input_details()
        #         self.insert_resume()
        #         self.process_form_inputs(form_input_details)
        #         self.reset_every_job_variable()
        # #! div_main ==> lever.co = job_description
        return
    
    def analyze_job_suitabililty(self):
        #Put here due to "greenhouse" but it's purpose is to hold job description webpage so the user can look back on!
        self.current_jobs_details["job_url"] = self.current_url
        self.soup_elements['soup'] = self.apply_beautifulsoup(self.current_url, "lxml")
        
        self.handle_job_description_webpage()
        user_fits_jobs_criteria = self.should_user_apply(self.soup_elements['opening_link_description'])
        job_fits_users_criteria = self.fits_users_criteria()
        
        if user_fits_jobs_criteria == True and job_fits_users_criteria == True:
            print("User is applying to this lever.co tabajo!!")
            #This clicks for us
            self.bottom_has_application_or_button(self.application_company_name)
            return 2
        # elif should_apply == False:
        #     return 
        else:
            print("\tHmmm that's weird ? it's neither button nor application")
            return 1
        
    def apply_to_job(self):
        time.sleep(3)
        current_url = self.browser.current_url
        #This is because lever has a new webpage for the job application but greenhouse doesn't
        if self.application_company_name == "lever":
            self.init_reset_webpage_soup_elements()
        #TODO: self.soup_elements  > > >  do something with the soup!!!
        self.soup_elements['soup'] = self.apply_beautifulsoup(current_url, "html")
        self.form_input_details = self.get_form_input_details(current_url)
        self.insert_resume()
        self.process_form_inputs(self.form_input_details)
        return 3
        
    #TODO: Because of this one all the pages need to be shifted! MOVE THIS TO 0! Then everything else + 1!!!
    def find_companys_internal_job_openings_URL(self):
        self.soup_elements['soup'] = self.apply_beautifulsoup(self.current_url, "lxml")
        self.search_for_internal_jobs_link()
        return 1
        
    
    # if (current_webpage == ApplicationOnly)   =>   attempt to find this companies CompanyJobOpenings url && if we do then go there and return "if not... idk I didn't get that far I guess"
        #REASON: We're not going to fill out a random application
    # elif (current_webpage == JobDescription)   =>   normal walk-through
    # elif (current_webpage == CompanyJobOpenings)   =>   return
    # elif (current_webpage == None)  =>   if (typeof(job_link) == list) try next link BUT if all are unsuccessfull THEN REMEMBER THIS COMPANY CAUSE THEY SUCK and we'll never apply again!
    #TODO: Change variable name ->  job_link
    def determine_current_page(self, job_link):
        print("determine_current_page()")
        soup = self.apply_beautifulsoup(job_link, "lxml")
        print("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        if self.application_company_name == "lever":
            webpage_body = soup.find('body')
            opening_link_application = soup.find('div', {"class": 'application-page'})
            opening_link_description = soup.find('div', {"class": 'posting-page'})
            opening_link_company_jobs = soup.find('div', {"class": "list-page"})
            
            if opening_link_application:
                print('-Application Page')
                self.soup_elements.update({
                    'soup': soup,
                    'webpage_body': webpage_body,
                    'opening_link_application': opening_link_application
                })
                return 2
            
            elif opening_link_description:
                print("-Job Description Page")
                self.soup_elements.update({
                    'soup': soup,
                    'webpage_body': webpage_body,
                    'opening_link_description': opening_link_description
                })
                return 1

            elif opening_link_company_jobs:
                print('-Job Listings Page')
                self.soup_elements.update({
                    'soup': soup,
                    'webpage_body': webpage_body,
                    'opening_link_company_jobs': opening_link_company_jobs
                })
                return 0
            #This return represents the link was indeed a "lever" webpage but something went wrong
                #TODO:Also returning job_link for logging purposes!
            return self.application_company_name, job_link
        elif self.application_company_name == "greenhouse":
            div_main = soup.find("div", id="main")
            #job_description_element = self.browser.find_element(By.ID, "content")
            
            next_elem = div_main.find_next()
            while next_elem:    #NOTE: REMEBER THIS DOESN'T INCREMENT next_elem SO IT'S THE SAME VALUE AS ABOVE!!!!
                if next_elem.name == "div" and (next_elem.get("id") == "flash-wrapper" or next_elem.get("id") == "flash_wrapper"):
                    print('-Job Listings Page V.1')
                    return 0
                elif (next_elem.name == "div" and next_elem.get("id") == "embedded_job_board_wrapper"):
                    print('-Job Listings Page V.2')
                    return 0
                elif (next_elem.name == "section" and next_elem.get("class") == "level-0"):
                    print('-Company Job Openings Page')
                    print("A while loop for this is perfect for this because there can be multiple <section class='level-0'>")
                    #TODO: for this one in the elif you have to look through all "level-0" sections!!
                    return 0
                elif next_elem.name == "div" and next_elem.get("id") in ["app-body", "app_body"]:
                    app_body = next_elem
                    header = next_elem.find("div", id="header")
                    content = next_elem.find("div", id="content")
                    
                    if header and content:
                        print("-Job Description Page")
                        self.soup_elements.update({
                            'soup': soup,
                            'div_main': div_main,
                            'app_body': app_body,
                            'header': header,
                            'content': content
                        })
                        return 1

                    break
                else:
                    next_elem = next_elem.find_next()
            #This return represents the link was indeed a "lever" webpage but something went wrong
                #TODO:Also returning job_link for logging purposes!
            return self.application_company_name, job_link
            
        print("2 possibilities for how the heck we ended up here:")
        print("\tOPTION 1) This webpage is neither a lever nor a greenhouse <best case scenario>")
        print("\tOPTION 1+1) Uhhhh either my code, the website, or my neighbor Roberto went crazy and there's absolutely no inbetween!")
        return
    
    def handle_application_webpage(self):
        if self.application_company_name == "lever":
            if not self.companys_internal_job_openings_URL:
                try:
                    #TODO: This is v what we want to avoid!!!
                    company_open_positions = self.soup_elements['soup'].find('a', {"class": "main-header-logo"})
                    application_webpage_html = self.soup_elements['soup'].find("div", {"class": "application-page"})
                    self.lever_co_banner(self.soup_elements['webpage_body'], self.soup_elements['soup'])
                except:
                    #TODO: Change this Error type!
                    raise ConnectionError("ERROR: Companies other open positions are not present")
        elif self.application_company_name == "greenhouse":
            print("I should never see this message ever in my life!")
    
    #TODO
    #! opening_link_description  =>  determine_current_page()
    def handle_job_description_webpage(self):
        if self.application_company_name == "lever":
            company_open_positions = self.soup_elements['soup'].find('a', {"class": "main-header-logo"})
            application_webpage_html = self.soup_elements['soup'].find("div", {"class": "application-page"})
            if not self.companys_internal_job_openings_URL:
                try:
                    self.lever_co_banner(self.soup_elements['webpage_body'], self.soup_elements['soup'])
                except:
                    #TODO: Change this Error type!
                    raise ConnectionError("ERROR: Companies other open positions are not present")
            
            #TODO: Finish this!!!
            #self.fits_users_criteria(  )
            
            self.scroll_to_element(self.soup_elements['opening_link_description'])
            #! TESTING  analyze_job_suitabililty  TESTING  analyze_job_suitabililty  TESTING  analyze_job_suitabililty
            return self.job_application_webpage[1]
            apply_to_job = self.should_user_apply(self.soup_elements['opening_link_description'])
            if apply_to_job == True:
                print("User is applying to this lever.co tabajo!!")
                #This clicks for us
                self.bottom_has_application_or_button(self.application_company_name)
                time.sleep(3)
                current_url = self.browser.current_url
                #TODO: self.soup_elements  > > >  do something with the soup!!!
                self.soup_elements['soup'] = self.apply_beautifulsoup(current_url, "html")
                self.form_input_details = self.get_form_input_details(current_url)
                self.insert_resume()
                self.process_form_inputs(self.form_input_details)
            elif should_apply == False:
                return 
            else:
                print("\tHmmm that's weird ? it's neither button nor application")
        elif self.application_company_name == "greenhouse":
            if not self.companys_internal_job_openings_URL:
                try:
                    self.greenhouse_io_banner(self.soup_elements['app_body'], self.soup_elements['header'], self.soup_elements['content'])    #TODO: return *job_title, company, location, ???*
                except:
                    #TODO: Change this Error type!
                    raise ConnectionError("ERROR: Companies other open positions are not present")
            
            #TODO: Finish this!!!
            #self.fits_users_criteria(  )
            
            #TODO: Find out if this is a good place to scroll too!
            self.scroll_to_element(self.soup_elements['content'])
            current_url = self.browser.current_url
            should_apply = self.should_user_apply(self.soup_elements['app_body'])
            if should_apply == True:
                self.bottom_has_application_or_button(self.application_company_name)
                time.sleep(3)
                print("User is applying to this greenhouse.io tabajo!!")
                self.form_input_details = self.get_form_input_details(current_url)
                self.insert_resume()
                self.process_form_inputs(self.form_input_details)
            elif should_apply == False:
                return
            else:
                print("\tHmmm that's weird ? it's neither button nor application")
        return
    
    
    
    
   
    
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!                                TOOLS                                          !
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    #***
    def apply_beautifulsoup(self, job_link, parser):
        print("apply_beautifulsoup()")
        #the way I learned how to do it
        if parser == "lxml":
            result = requests.get(job_link)
            content = result.text
            soup = BeautifulSoup(content, "lxml")
        #used for form_input_details()
        if parser == "html":
            page = requests.get(job_link)
            result = page.content
            soup = BeautifulSoup(result, "html.parser")           
        return soup
    
    #***
    def scroll_to_element(self, element):
        print("scroll_to_element()")
        # Check if the input element is a BeautifulSoup element
        if isinstance(element, Tag):
            # Extract the tag name
            tag_name = element.name
            print("  ", {tag_name})
            
            # Extract the attributes
            attrs = element.attrs
            css_selectors = [f"{tag_name}"]
            
            # Convert attributes to CSS selectors
            for attr, value in attrs.items():
                if isinstance(value, list):
                    value = " ".join(value)
                    css_selectors.append(f"[{attr}='{value}']")
                    
                css_selector = "".join(css_selectors)
                print("  ", end="")
                print(css_selector)
                
                # Find the same element using Selenium
                element = self.browser.find_element(By.CSS_SELECTOR, css_selector)
                
        self.browser.execute_script("arguments[0].scrollIntoView();", element)
        print("  Scrolled to this place...")
        time.sleep(3)
        return
    
    #***
    def dismiss_random_popups(self):
        wait = WebDriverWait(self.browser, 10)
        try:
            overlay_close_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.cc-desktop button.cc-dismiss')))
            # Wait a bit before clicking the button
            time.sleep(2)
            # Check if the button is displayed and enabled
            if overlay_close_button.is_displayed() and overlay_close_button.is_enabled():
                overlay_close_button.click()
            else:
                print("The 'Dismiss' button is not interactable. Skipping click.")
                print("Button's outer HTML:", overlay_close_button.get_attribute('outerHTML'))
        except TimeoutException:
            # The 'overlay'/pop-up didn't appear within the timeout, so continue
            print("ok that took a while because I thought there would be a pop-up... ONWARD I suppose!")
        except ElementNotInteractableException:
            # The button was found but it was not interactable
            print("Failed to click the 'Dismiss' button because it's not interactable.")
            print("Button's outer HTML:", overlay_close_button.get_attribute('outerHTML'))
    
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!                                                                               !
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    

    
    
    
    


    
    
    
    
    # updated_google_search_results_links
    # previously_applied_links
    

    
    
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!                                FILTER                                         !
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def filter_companys_current_job_opening_urls(self):
        #This filters company_job_openings BUT only removes duplicates && everything previously already looked at!!
        self.list_of_links = self.JobSearchWorkflow_instance.ensure_no_duplicates(self.list_of_links)
        #Since I collect all the links for a company prior I THINK this might no longer be necessary!?!?!?
        #todays_jobs_applied_to_URLs = self.JobSearchWorkflow_instance.get_job_links_users_applied_to(self.sessions_applied_to_info)
        if not self.sibling_company_job_links:
            self.list_of_links = self.check_google_search_links()
        #self.list_of_links = self.JobSearchWorkflow_instance.filter_out_jobs_user_previously_applied_to(self.list_of_links, todays_jobs_applied_to_URLs)  # < < < previously applied to positions
        self.list_of_links = self.JobSearchWorkflow_instance.filter_out_jobs_user_previously_applied_to(self.list_of_links, self.JobSearchWorkflow_instance.previously_applied_to_job_links)
    
    def check_google_search_links(self):
        new_link_list_lol = []
        for extra_google_links in self.sibling_company_job_links:
            if self.companys_internal_job_openings_URL == extra_google_links:
                continue
            for company_internal_jobs in self.list_of_links:
                if extra_google_links == company_internal_jobs:
                    continue
            new_link_list_lol.append(extra_google_links)
        return (self.list_of_links + new_link_list_lol)
    
    #TODO: I put this one in determine_current_page()
    #IDEA: Maybe like don't surpass 5 applications to the same company??
    def fits_users_criteria(test_elements_uniqueness, *args):
        ultimate_lists_checker = []
        for arg in args:
            ultimate_lists_checker.extend(arg)                      #WORKS for job_title && links
        for unacceptable_element in ultimate_lists_checker:
            if unacceptable_element in test_elements_uniqueness:
                return False
        return True
    

    def check_users_basic_requirements(self, company_job_title, job_location, job_workplaceType):
        if self.users_job_search_requirements['entry_level'] == True:
            if self.users_basic_requirements_experience_level(company_job_title) == False:
                return False
        
        if self.user_basic_requirements_location_workplaceType(job_location, job_workplaceType):
            return False

    def users_basic_requirements_job_title(self, company_job_title):
        return any(desired_job in company_job_title for desired_job in self.users_job_search_requirements['job_title'])

    def users_basic_requirements_experience_level(self, company_job_title):
        return any(experience_keyword in company_job_title for experience_keyword in self.prior_experience_keywords)
    
    def get_experience_level(self, company_job_title):
        for experience_keyword in self.prior_experience_keywords:
            if experience_keyword in company_job_title:
                return experience_keyword

    def user_basic_requirements_location_workplaceType(self, company_job_location, company_job_workplaceType):
        # Job location is unknown OR 'at the bare minimum'(due to working permits) countries don't match up
        if not company_job_location or company_job_location.lower().country() not in self.users_job_search_requirements['user_preferred_locations']:
            return False
        
        # User has specific location requirements
        if company_job_location not in self.users_job_search_requirements['user_preferred_locations']:
            return False
        
        if not company_job_workplaceType or company_job_workplaceType.lower() == "unknown":
            return False
        
        # edge cases
        if company_job_workplaceType.lower() == 'in-office with occasional remote':     #could just refer to this as travel
            if 'in-office' in self.users_job_search_requirements['user_preferred_workplaceType'] or 'remote' in self.users_job_search_requirements['user_preferred_workplaceType']:
                return True
            else:
                return False
            
        if company_job_workplaceType.lower() == 'hybrid with rare in-office':
            if 'hybrid' in self.users_job_search_requirements['user_preferred_workplaceType'] or 'remote' in self.users_job_search_requirements['user_preferred_workplaceType']:
                return True
            else:
                return False
        
        #standard scenario    
        if company_job_workplaceType.lower() == 'remote':
            return True
        
        if company_job_workplaceType.lower() == 'hybrid':
            if 'hybrid' in self.users_job_search_requirements['user_preferred_workplaceType'] and 'in-office' in self.users_job_search_requirements['user_preferred_workplaceType']:
                return True
            else:
                return False
            
        if company_job_workplaceType.lower() == 'in-office':
            if 'in-office' in self.users_job_search_requirements['user_preferred_workplaceType']:
                return True
            else:
                return False
            
        print("Yo dog some crapola went wrong or somethin dog")
        return False
    
    
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!                                                                               !
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    
    #TODO: This goes to all the links!!
    '''
    def troubleshoot_xpath(self):
        for link in self.list_of_links:
            try:
                self.browser.get(link)
                time.sleep(2)
                job_title = self.browser.title
                print(f"Scraping job: {job_title}")

                # Search for the Google search name in the page
                google_search_name = job_title.split("-")[0].strip()
                print(f"Searching for: {google_search_name}")
                selenium_google_link = self.browser.find_element(By.XPATH, f'//ancestor::a/h3[not(descendant::br)][text()="{google_search_name}"]')
                print("Found search result")

                # Click on the Google search result link
                selenium_google_link.click()
                print("Clicked on the search result link")

                # Wait for the page to load and switch to the new tab
                WebDriverWait(self.browser, 10).until(EC.number_of_windows_to_be(2))
                self.browser.switch_to.window(self.browser.window_handles[-1])
                print("Switched to new tab")

                # Perform actions on the job page
                self.scrape_job_page()

                # Close the new tab and switch back to the search results tab
                self.browser.close()
                self.browser.switch_to.window(self.browser.window_handles[0])
                print("Closed new tab and switched back to search results tab")

            except NoSuchElementException:
                print(f"No search result found for: {google_search_name}")
                continue
    '''



    # STAGE 1: Figure out where ever the heck we are; if we happen to be in a position to fill out a job application then great do that, then get to company_job_openings (Use the header methods to accomplish this!!)  
    # STAGE 2: Once at the Company's Job Listings page -> GO THROUGH ALL THE JOBS   ALL WHILE  1)collecting all the jobs for the user AND 2) collect data for Google Sheets (filterings should take place) return back to CompanyWorkflow
    # STAGE 3: 
    # STAGE :
    # STAGE :
    # STAGE :
    # STAGE :
    





'''
        if opening_link_application:
            print('-Application Page')
            self.soup_elements.update({
                'soup': soup,
                'webpage_body': webpage_body,
                'opening_link_application': opening_link_application
            })
            return self.job_application_webpage[1]
        
        elif opening_link_description:
            print("-Job Description Page")
            self.soup_elements.update({
                'soup': soup,
                'webpage_body': webpage_body,
                'opening_link_description': opening_link_description
            })
            return self.job_application_webpage[0]

        elif opening_link_company_jobs:
            print('-Job Listings Page')
            self.soup_elements.update({
                'soup': soup,
                'webpage_body': webpage_body,
                'opening_link_company_jobs': opening_link_company_jobs
            })
                        if header and content:
                            print("-Job Description Page")
                            self.soup_elements.update({
                                'soup': soup,
                                'div_main': div_main,
                                'app_body': app_body,
                                'header': header,
                                'content': content
                            })
                            return self.job_application_webpage[0]
self.soup_elements['webpage_body']       self.soup_elements['soup']       self.soup_elements['']
'''
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!                   INDIVIDUAL COMPANY-WORKFLOW STEPS                           !
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    #TODO: Make sure this works for when there are no links!! ALSO, maybe add a special case for "Don't see your job"/"General" application
    #def company_job_openings()
    #***
    def collect_companies_current_job_openings(self, soup, div_main, application_company_name):
        print("collect_companies_current_job_openings()")
        print("Application Company = " + application_company_name)
        current_url = self.browser.current_url
        
        if application_company_name == 'lever':
            postings_wrapper = soup.find('div', class_="postings-wrapper")
            postings_group_apply = postings_wrapper.find_all('div', class_=lambda x: x and ('postings-group' in x or 'posting-apply' in x))
            for section in postings_group_apply:
                self.init_current_jobs_details()
                print(section)
                company_department = section.find('div', class_='large-category-header').text
                if company_department:
                    print(company_department)
                if section.name == 'div' and section.get('class') == 'posting-apply':
                    job_opening_href = section.next_sibling
                    if job_opening_href.name == 'a' and job_opening_href.get('class') == 'posting-title':
                        #GET RID OF THESE???????
                        button_to_job_description = job_opening_href
                        print("button_to_job_description = ", button_to_job_description)
                        #GET RID OF THESE???????
                        job_url = self.construct_url_to_job(current_url, job_opening_href)
                        job_title = job_opening_href.find('h5').text
                        print("job_title = ", job_title)

                        if self.users_basic_requirements_job_title(job_title) == False:
                            continue
                        
                        experience_level = self.get_experience_level(job_title)

                        span_tag_location = job_opening_href.find('span', {'class', 'sort-by-location'})
                        span_tag_company_team = job_opening_href.find('span', {'class': 'sort-by-team'})
                        span_tag_workplaceType = job_opening_href.find('span', {'class': 'workplaceTypes'})

                       
                        job_location = span_tag_location.text if span_tag_location else None
                        #TODO: Find out what the heck this team is!!!
                        #company_team = span_tag_company_team.text if span_tag_company_team else None
                        job_workplaceType = span_tag_workplaceType.text if span_tag_workplaceType else None
                            
                            
                if self.check_users_basic_requirements(job_title, job_location, job_workplaceType):
                    self.current_jobs_details.update({
                        'company_department': company_department,
                        'job_url': job_url,
                        'job_title': job_title,
                        'experience_level': experience_level,
                        'job_location': job_location,
                        'job_workplaceType': job_workplaceType
                    })
                    if not experience_level:
                        self.list_of_links.append(job_url)

                self.print_companies_internal_job_opening("company_job_openings", application_company_name, JobTitle=job_title, JobLocation=job_location, WorkPlaceTypes=job_workplaceType, CompanyDepartment=company_department, JobTeamInCompany=span_tag_company_team, JobHREF=job_url, ButtonToJob=button_to_job_description)
            return
            
        elif application_company_name == 'greenhouse':
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
                    #GET RID OF THESE???????
                    button_to_job_description = job_opening_href
                    print("button_to_job_description = ", button_to_job_description)
                    #GET RID OF THESE???????
                    if job_opening_href:
                        job_title = job_opening_href.text
                        print("job_title = ", job_title)

                        if self.users_basic_requirements_job_title(job_title) == False:
                            continue
                        
                        experience_level = self.get_experience_level(job_title)

                        job_url = self.construct_url_to_job(current_url, job_opening_href)

                        span_tag_location = job_opening.find('span', {'class', 'location'})
                        
                        job_location = span_tag_location.text if span_tag_location else None
                        print("job_location = ", job_location)
                        #job_opening_href.click()
                        
                if self.check_users_basic_requirements(job_title, job_location, job_workplaceType):
                    self.current_jobs_details.update({
                        'job_url': job_url,
                        'job_title': job_title,
                        'experience_level': experience_level,
                        'job_location': job_location,
                        'job_workplaceType': job_workplaceType
                    })
                    if not experience_level:
                        self.list_of_links.append(job_url)
                self.print_companies_internal_job_opening("company_job_openings", application_company_name, JobTitle=job_title, JobLocation=job_location, ButtonToJob=button_to_job_description)
        return
    

    def print_companies_internal_job_opening(*args, **kwargs):
        print('\n\n\n')
        print('----------------------------------------------------------------------------------------------------')
        print("print_company_job_openings()")
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
    
    #The purpose of this method is pretty much only finding and retrieving the companies' other open positions url!!!
    #TODO:   list_of_links  [ ]
    #***
    def search_for_internal_jobs_link(self):
        print("search_for_internal_jobs_link()")
        if self.application_company_name == "lever":
            print("\ngreenhouse_co_banner()")
            links_in_header = []
            print("\nThese are the links/elements that lead to this companies other available Job Openings:")
            current_url = self.browser.current_url
            print("Current URL: " + current_url)
            links_in_header.append(current_url)
            webpage_header = self.soup_elements['webpage_body'].find('div', {"class": 'main-header-content'})
            company_open_positions_a = webpage_header.find('a', {"class": "main-header-logo"})
            #! RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX
            #print("Selenium Click => Companies other Job Openings: " + company_open_positions_a)
            if isinstance(company_open_positions_a, str):
                print("Selenium Click => Companies other Job Openings: " + company_open_positions_a)
            else:
                print("Selenium Click => Companies other Job Openings: " + str(company_open_positions_a))
            #! RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX RECENT FIX

            try:
                if company_open_positions_a['href']:
                    company_open_positions_href = company_open_positions_a['href']
                    print("Webpage's Header link: " + company_open_positions_href)
                    list_of_links = company_open_positions_href
                    print("Webpage's Header link: " + company_open_positions_href)
                    links_in_header.append(list_of_links)
            except:
                print("This company's webpage is dumb anyways! Trust me they would've probably overworked you anyways.")
            links_in_header.append(company_open_positions_a)
            self.check_banner_links(links_in_header)
            return
        
        #line 570 #elif child.name == "a"
        #if ("button" in child.get("class")) => remember !BUTTON! to click
        elif self.application_company_name == "greenhouse":
            print("\ngreenhouse_io_banner()")
            a_fragment_identifier = None
            company_other_openings_href = None
            
            first_child = True
            searched_all_a = False
            string_tab = '\n'
            for child in self.soup_elements['header'].children:
                if first_child:
                    first_child = False
                    continue
                elif child == string_tab:
                    #? continue
                    pass
                if child.name == "h1" and "app-title" in child.get("class"):
                    self.current_jobs_details["job_title"] = child.get_text().strip()
                elif child.name == "span" and  "company-name" in child.get("class"):
                    self.current_jobs_details["company_name"] = child.get_text().strip()
                elif child.name == "a" and not searched_all_a:
                    header_a_tags = self.soup_elements['header'].find_all('a')
                    for head_a_tag in header_a_tags:
                        if '/' in head_a_tag['href']:
                            company_other_openings_href = head_a_tag
                        elif '#' in head_a_tag['href']:
                            a_fragment_identifier = head_a_tag
                        elif head_a_tag == None:
                            logo_container = self.soup_elements['app_body'].find('div', class_="logo-container")
                            company_openings_a = logo_container.find('a')
                            company_other_openings_href = company_openings_a['href']
                            searched_all_a = True

                elif child.name == "div" and "location" in child.get("class"):
                    self.current_jobs_details["job_location"] = child.get_text().strip()
            if company_other_openings_href == None:
                #!!!!!!!!!!!! ERROR HANDLING !!!!!!!!!!!!
                # if a_fragment_identifier is None:
                #     a_fragment_identifier = 'Nothing here doofus!'
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                self.print_companies_internal_job_opening("greenhouse_io_banner()", "greenhouse", JobTitle=self.company_job_title, CompayName=self.company_name, JobLocation=self.company_job_location, JobHREF="Couldnt Find", LinkToApplication_OnPageID=a_fragment_identifier)
            else:
                self.print_companies_internal_job_opening("greenhouse_io_banner()", "greenhouse", JobTitle=self.company_job_title, CompayName=self.company_name, JobLocation=self.company_job_location, JobHREF=company_other_openings_href, LinkToApplication_OnPageID=a_fragment_identifier)
            return
            #self.greenhouse_io_content(app_body, content)
            # if a_fragment_identifier == None:
            #     return self.company_job_title, self.company_name, self.company_job_location, company_other_openings_href
            # else:
            #     return self.company_job_title, self.company_name, self.company_job_location, company_other_openings_href, a_fragment_identifier
        
        
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

    



    
    #TODO: Lots of work needs to be done here!!!
    # This method is checking the links present in the header of a web page. It takes a list of
    # links as input and iterates through each link. If the link is the firstlink and the company
    # name is "lever", it tries to adjust the job link using the try_adjusting_this_link() method
    # and sets list_of_other_jobs_keyword to 'list-page'.

    # If the link is the first link and the company name is "greenhouse", it sets
    # list_of_other_jobs_keywords to an empty string and sets first_link to False. It then opens
    # each link in a new window using execute_script() method of the browser object and switches
    # to each window using switch_to.window() method.

    # For each window, it checks if list_of_other_jobs_keyword is present in the page source. If
    # it is present, it sets company_open_positions_link to the current link and returns. If
    # company_open_positions_link is still None after checking all the links, it clicks on
    # company_open_positions_a and waits for 3 seconds.
    #***
    def check_banner_links(self, links_in_header):
        print("check_banner_links()")
        #! CANT SET VALUES TO LOCAL VARIABLES  REMEMBER!!!!!...  except for booleans I guess?
        first_link = True
        list_of_other_jobs_keyword
        for header_link in links_in_header[:-1]:
            if first_link == True and "lever" == self.application_company_name:
                self.try_adjusting_this_link(header_link)    #! <- try_adjusting_this_link() returns a link!!
                list_of_other_jobs_keyword = 'list-page'
                first_link = False
            elif first_link == True and "greenhouse" in self.application_company_name:
                
                
                
                
                #self.try_adjusting_this_link(header_link)    #! <- try_adjusting_this_link() returns a link!!
                
                
                
                list_of_other_jobs_keywords = ''    #I think I just need to add a keyword here => just like lever - 'list-page'
                first_link == False
            self.browser.execute_script("window.open('{}', '_blank');".format(header_link))
            for handle in self.browser.window_handles:
                self.browser.switch_to.window(handle)
                if list_of_other_jobs_keyword in self.browser.page_source:
                    self.company_open_positions_link = header_link
                    return
        print("Hmmmm this is unexpected. I must be dumb...")
        time.sleep(1)
        print("Not like you the user; I mean me the programmer...      ", end="")
        time.sleep(1)
        print("hmmmm...")
        time.sleep(2)
        print("You probably suck too though, don't think you dont't :)")
        time.sleep(1)
        if (self.company_open_positions_link == None):
            #self.company_open_positions_a.click()
            links_in_header[-1].click()
            time.sleep(3)
            #TODO
            #!  YOU NEED TO CHECK IF IT WAS SUCCESSFUL!!!!!
            #original_link == self.browser.current_link
    
    #***
    def try_adjusting_this_link(self, adjust_this_link):
        print("try_adjusting_this_link()")
        if self.application_company_name == 'lever':
            adjusting_link = adjust_this_link.find('jobs.lever.co/') + len('jobs.lever.co/')
            still_adjusting = adjust_this_link.find('/', adjusting_link) + 1
            # if self.is_absolute_path(still_adjusting):
            #     print("We know two things 1)This is in fact an href 2)This does lead somewhere")
            # else:
            #     #!IDEA: After the 'lever' and 'greenhouse' check wrap all this in a while loop && try a couple things!!
            #     print("I really have not 1 clue what to do here")
            link_adjusted = adjust_this_link[:still_adjusting]
            print(link_adjusted)
            adjust_this_link = link_adjusted
            print(adjust_this_link)
        if self.application_company_name == 'greenhouse':
            adjusting_link = adjust_this_link.find('greenhouse.io/') + len('greenhouse.io/')
            still_adjusting = adjust_this_link.find('/', adjusting_link) + 1
            link_adjusted = adjust_this_link[:still_adjusting]
            print(link_adjusted)
            adjust_this_link = link_adjusted
            print(adjust_this_link)
        time.sleep(2)
        return adjust_this_link
    
    def construct_url_to_job(self, current_url, job_opening_href):
        # v Maybe for Selenium?
        button_to_job_description = job_opening_href
        print("button_to_job_description = ", button_to_job_description)
        job_link = job_opening_href.get('href')
        print("job_link = ", job_link)
        try:
            if self.is_absolute_path(job_link) == False:
                print("Ummm honestly I would have no idea what to do here!!")
        except ConnectionError:
            print(r"Error {e}")
        
        domain_name = self.try_adjusting_this_link(current_url)
        print("domain_name = ", domain_name)
        job_path = job_opening_href.get('href')
        print("job_path = ", job_path)
        job_url = domain_name + job_path
        print("job_url = ", job_url)
        return job_url
    
    #! NOT RELATED TO ANYTHING !!!!
    #TODO: Might be apart of the check_banner_links || try_adjusting_this_link
    #***
    def is_absolute_path(self, href):
        print("is_absolute_path()")
        parsed_url = urlparse(href)
        print("The href value is: ", end="")
        print(parsed_url)
        return bool(parsed_url.netloc)
    #! NOT RELATED TO ANYTHING !!!!
    
    
    #TODO: v = [is_absolute_path() + construct_url_to_job() + try_adjusting_this_link() + check_banner_links()]
    def find_internal_job_listings_url(browser):
        # Get the current page source
        html = browser.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find the header and logo-container elements
        header = soup.find('div', {'id': 'header'})
        logo_container = soup.find('div', {'class': 'logo-container'})

        # Initialize the link to None
        link = None

        # Check if the header or logo-container exists and contains a link
        if header:
            link = header.find('a', href=True)
        elif logo_container:
            link = logo_container.find('a', href=True)

        # If a link was found, get the href attribute
        if link:
            href = link['href']

            # Check if the href is an absolute URL
            if not href.startswith('http'):
                # If not, construct the absolute URL
                base_url = browser.current_url
                href = urljoin(base_url, href)

            return href

        # If no link was found, return None
        return None
    
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!                                                                               !
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   
    
    
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    
    
    
    

    
    
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!                        USERS COMPANY-WORKFLOW STEPS                           !
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    #everything_about_job = app_body.get_text()
    #should_user_apply(everything_about_job)
    #greenhouse(job_description) => app_body
    def should_user_apply(self, job_description):
        print("should_user_apply()")
        print("Welcome fair maiden this company has gathered to make decisions based on your skin color... please after you!")
        #FILTER: keywords (industry experience//////)
        everything_about_job = job_description.get_text()

        #print(everything_about_job)
        #experience_needed = r"\b\d+\s*(year|yr)s?\s+of\s+experience\b"
        experience_needed = "You must be a diety! Being a demigod or demigoddess is literally embarrassing... just go back to coloring if this is you. Literally useless & pathetic ewww"
        if re.search(experience_needed, everything_about_job):
            print("Experience requirement found!")
            #print(re.search(experience_needed, everything_about_job))
            return False
        else:
            print("No experience requirement found!")
            #print(re.search(experience_needed, everything_about_job))
            return True
        
    def bottom_has_application_or_button(self, application_company_name):
        print("bottom_has_application_or_button()")
        soup = self.apply_beautifulsoup(self.browser.current_url, "html")
        if application_company_name == "lever":
            a_tag_butt = soup.find('a', {'data-qa': ['btn-apply-bottom', 'show-page-apply']})
            div_tag_butt = soup.find('div', {'data-qa': 'btn-apply-bottom'})
            application_at_bottom = soup.find("div", id="application")
            print("\nLever: Application at bottom or <button>")
            if a_tag_butt:
                print("\tPress button to go to application")
                xpath_selector = f"//a[@data-qa='{a_tag_butt['data-qa']}']"
                print(f"xpath_selector: {xpath_selector}")
                apply_button = self.browser.find_element(By.XPATH, xpath_selector)
                self.scroll_to_element(apply_button)
                time.sleep(1)
                print("apply_button: ", end="")
                print(apply_button)
                apply_button.click()
                time.sleep(2)
            elif div_tag_butt:
                print("\tlever: Press button to go to application")
                apply_button = self.browser.find_element(By.XPATH, f"//div[@data-qa='{a_tag_butt['data-qa'][0]}']")
                self.scroll_to_element(apply_button)
                time.sleep(1)
                apply_button.click()
                time.sleep(3)
            elif application_at_bottom:
                print("\tApplication at bottom of page")
                self.scroll_to_element(application_at_bottom)
            return
            
        elif application_company_name == "greenhouse":
            application = soup.find("div", id="application")
            apply_button_list = None
            try:
                apply_button_list = self.browser.find_element(By.XPATH, "//button[text()='Apply Here' or text()='Apply Now' or text()='Apply for this job']")
            except NoSuchElementException:
                pass
            print("\nGreenhouse: Application at bottom or <button>")
            if application:
                self.scroll_to_element(application)
                print("\tApplication at bottom of page")
                time.sleep(1)
            elif apply_button:
                apply_button = apply_button_list
                print("apply_button options:", end="") 
                print(apply_button)

                self.scroll_to_element(apply_button)
                print("\tPress button to go to application")
                time.sleep(1)
                apply_button.click()
                time.sleep(3)
            return
    
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!                                                                               !
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   
    
    
    
    

    
    
    
    #Apart of insert_resume() but   BUT the variable it is set = to I don't think is ever used! (Meaning this code is now useless)
    def get_input_tag_elements(self):
        """
        Returns a list of tuples with input element ID, type and visibility status
        """
        input_elements = self.browser.find_elements(By.TAG_NAME, 'input')
        inputs_info = []
        for input_element in input_elements:
            input_id = input_element.get_attribute('id')
            input_type = input_element.get_attribute('type')
            is_hidden = input_element.get_attribute('type') == 'hidden' or not input_element.is_displayed()
            inputs_info.append((input_id, input_type, is_hidden))
        return inputs_info

    def find_visible_input(self, selector):
        input_element = self.browser.find_element(By.CSS_SELECTOR, selector)
        is_hidden = input_element.get_attribute('type') == 'hidden' or not input_element.is_displayed()
        if is_hidden:
            self.browser.execute_script("arguments[0].style.display = 'block';", input_element)
            is_hidden = input_element.get_attribute('type') == 'hidden' or not input_element.is_displayed()
        return input_element, not is_hidden

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!       REMEMBER TO COUNT THE NUMBER OF OPEN SENIOR > ROLES AVAILABLE           !
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    #! FIND AND ATTACH RESUME 1st B/C AUTOFILL SUCKS
    def insert_resume(self):
        print("\ninsert_resume()")
        #resume_path = self.users_information.get('WORK_RESUME_PATH')
        resume_path = self.users_information.get('RESUME_PATH')
        print(resume_path)
        
        if self.application_company_name == 'greenhouse':
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
                print("That's so silly! Can't scroll")
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
            self.dismiss_random_popups()
                        #self.browser.execute_script("arguments[0].scrollIntoView();", resume_file_input)
            #resume_upload_button = self.browser.find_element(By.CSS_SELECTOR, 'button.visible-resume-upload')
            #resume_upload_button = self.browser.find_element(By.CSS_SELECTOR, 'button[aria-describedby="resume-allowable-file-types"]')
            wait = WebDriverWait(self.browser, 10)
            #overlay_close_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.close-overlay')))
            #overlay_close_button.click()
            resume_upload_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-describedby="resume-allowable-file-types"]')))
            print("--------------------------------------------------------")
            print(resume_upload_button)
            print("--------------------------------------------------------")
            #print()
            print("6")
            if resume_upload_button:
                time.sleep(1)
                print("8")
                input_elements = self.get_input_tag_elements()
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
        print("14 Holy Hole")
        return
    
    def get_label(self, input_element):
        # Check for the special case: 'button' and 'submit application' in input_element
        input_element_str = str(input_element).lower()
        if 'button' in input_element_str and 'submit application' in input_element_str:
            return 'Submit Application'
        
        if input_element.get('type') == 'radio':
            label = self.find_radio_label(input_element)
            return label
        
        if input_element.get('type') == 'checkbox':
            div_parent, parents_text = self.get_div_parent(input_element)
            if div_parent == 'None' or parents_text == 'None':
                pass
            elif div_parent and parents_text:
                #return div_parent, parents_text
                checkbox_values = [div_parent, parents_text]
                return checkbox_values

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
                
        # Case 6: Checks if the input element has an 'aria-label' meaning it's dynamic so goes & searches
        # all previous label containers to see if any have text values that are equal to the aria-label' 
        if not label:
            if 'aria-label' in input_element.attrs:
                aria_label_match = None
                parent_label = input_element.find_previous('label')
                aria_label_value = input_element["aria-label"]
                if parent_label.text.strip() == aria_label_value:
                    aria_label_match = True
                if aria_label_match:
                    dynamic_label = aria_label_value + " (dynamic " + input_element.get('type') + ")"
                    if dynamic_label:
                        return dynamic_label
                elif aria_label_match == None:
                    return aria_label_value
                        
        # Case 7: Checks if the input element's style attribute is equal to 'display: none;' meaning it's
        # dynamic so goes & searches for the most previous label container to specify its text value is dynamic
        if not label:
            if input_element.get('style') == 'display: none;':
                previous_input = input_element.find_previous('input')
                if previous_input:
                    parent_label = previous_input.find_previous('label')
                    dynamic_label = parent_label.text.strip() + " (dynamic " + input_element.get('type') + ")"
                    if dynamic_label:
                        return dynamic_label
                    
        # Case 8: Special case for Resume/CV
        if not label and self.one_resume_label == False:
            found_attach = False
            parent_label = input_element.find_previous('label')
            #print(f"----parent_label ========>>>>> {parent_label}")
            label = parent_label
            self.one_resume_label = True
            #TODO: This whole thing is pee pee poo poo
            current_element = input_element
            while current_element:
                if isinstance(current_element, NavigableString) and 'attach' in str(current_element).lower():
                    found_attach = True
                    break
                current_element = current_element.next_sibling
            # Traverse up from the specific_element and find the label tag
            if found_attach:
                label_tag = input_element.find_previous('label')
                if label_tag:
                    # Check if the immediate child is a text value
                    first_child = label_tag.contents[0]
                    if isinstance(first_child, NavigableString) and first_child.strip():
                        holey_holes = first_child.strip()
                    else:
                        # Check if it has a child element and if it does, save that child's text value
                        for child in label_tag.children:
                            if not isinstance(child, NavigableString):
                                holey_holes = child.get_text(strip=True)
                                break
                    #print(f"Text value of the label: {holey_holes}")
                    label = holey_holes
            else:
                print("No sibling found with the 'attach' keyword.")
                #print("Just to remember input_element = ")
                #print(input_element)

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
    
    #OG: print_form_heirarchy()
    def find_radio_label(self, element, stop_level=5):
        current_level = 0
        while (current_level <= stop_level):
            print(f"Level {current_level}:")
            if current_level == 0 or current_level == 5:
                if current_level == 0:
                    print(element.prettify())
                if current_level == 5:
                    sauce = element.next_element.get_text(strip=True)
                    print(sauce)
                    return sauce
            element = element.parent
            current_level += 1

    def get_div_parent(self, input_element):
        parent_element = input_element.find_previous(lambda tag: any('question' in class_name for class_name in tag.get('class', [])))
        if parent_element:
            current_element = parent_element.next_element
            while current_element:
                if isinstance(current_element, NavigableString) and current_element.strip():
                    parents_text = current_element.strip()
                    break
                current_element = current_element.next_element
        else:
            print("Craig would be dissapointed in you...    you maget!")
            
        input_tags = input_element.name
        correct_parent = None
        count = 0
        while correct_parent:
            correct_parent = parent_element.find_all(input_tags)     #[, {'type': }]
            if correct_parent:
                parent_element = correct_parent
                break
            parent_element = parent_element.next_sibling
            if count > 4:
                break
            print(count)
            count =+ 1
        return parent_element, parents_text

    #! Maybe include 2 parameters and check if url = None then skip beautifulsoup part!!
    def get_form_input_details(self, url):
        #TODO: GET RID OF THIS AS SOON AS POSSIBLE!!!!
        self.one_resume_label = False
        
        print("\nget_form_input_details()")
        print("URL = " + url)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'lxml')

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
            if input_type not in ['text', 'email', 'password', 'select', 'radio', 'checkbox', 'textarea', 'button', 'file'] and input_id != 'education_school_name':
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
                
                # Call get_label for the entire radio button group
                input_label = self.get_label(field)
                
            elif input_type == 'checkbox':
                if field in processed_radios:
                    continue
                
                #! values - different -> sometimes value attr or in search next element for text_value!!
                #div_parent, parents_text = self.get_label(field)
                checkbox_values = self.get_label(field)
                print("SWEET ODIN'S RAVEN ITS A checkbox A... A checkbox I SAY... GOSH DARN YOU LISTEN TO ME ITS A checkbox!!!")
                print("also the .get_label() appeared to work and has been returne Woodstock man animal...     Korny poo's ewww")
                print("checkbox_values = ", checkbox_values)
                div_parent = checkbox_values[0]
                print("div_parent = ", div_parent)
                parents_text = checkbox_values[1]
                print("parents_text = ", parents_text)
                values = []
                input_label = parents_text
                checkbox_group = div_parent.find_all('input', {'type': [input_type, "text", "textarea"]})
                input_html = ''.join([str(checkbox).strip() for checkbox in checkbox_group])
                for index, input_element in enumerate(checkbox_group):
                    parent_label = input_element.find_previous('label')
                    if input_element.get('type') == 'text':
                        values.append(parent_label.text.strip() + "(dynamic)")
                        continue
                    values.append(parent_label.text.strip())
                    processed_radios.add(input_element)

            else:
                # Call get_label for other input types
                input_label = self.get_label(field)

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
        print("Tyrants")
        time.sleep(6)
        self.print_form_details(form_input_details)
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
        
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!                                                                               !
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    
    #https://boards.greenhouse.io/blend/jobs/4870154004
    #https://boards.greenhouse.io/dice/jobs/6594742002
    #https://jobs.lever.co/atlassian/013b099b-85b2-4527-a2d4-18179b0a1247/apply
    #https://jobs.lever.co/gametime/58aef93e-7799-4ba0-bea9-e848520db151/apply
    #https://boards.greenhouse.io/zealcareers/jobs/4873035004
    
    
    
    
    
    
    
    

    
    
    

    
    
#Fiesty
        # def fill_form(self, form_input_details):
        # print("\nfill_form()")
        # for i, input_data in enumerate(form_input_details):
        #     print(f"Processing Input {i}: ...")

        #     # Check if it's a special case
        #     special_expected_user_input = self.is_special_case(input_data)
        #     if special_expected_user_input:
        #         print(f"Input {i}: a special case -> {special_expected_user_input}")

        #     # Extract label from the input_data
        #     label = input_data['label']

        #     # Handle custom rules or get matching key if present
        #     key = self.get_matching_key_if_present(label, special_expected_user_input)

        #     if key:
        #         # Get value from the users_information dictionary
        #         value = self.users_information[key]

        #         if special_expected_user_input == 'is_multiple_choice':
        #             # if multiple values are expected, we'll assume value is a list
        #             for v in value:
        #                 self.browser.find_element(label).send_keys(v)
        #                 # Add additional logic here to handle multiple choice selections
        #         elif special_expected_user_input == 'is_file':
        #             # handle file upload
        #             self.browser.find_element(label).send_keys(value)  # assuming value is file path
        #         else:
        #             # Fill in the form
        #             self.browser.find_element(label).send_keys(value)
        #     else:
        #         print(f"No matching key found for label {label}")
        # print("eff that question")
        # time.sleep(5)
#Kittens 

    
    
    

    
    def print_form_input_extended(self):
        print("\n\n\ndouble_check_before_fill_in_form()")
        
        print('--------------------------------------------')
        print("Form Input Extended: ")
        for key, value in self.form_input_extended.items():
            print(f"{key}: {value}")
        print('--------------------------------------------')
        print("\n")
    
    def extract_css(self, input_data_html):
        soup = BeautifulSoup(input_data_html, 'lxml')
        print("soup = ", soup)
        body_children = soup.body.contents
        for child in body_children:
            print('element = ', child)
            if child.get('id'):
                identifier = child.get('id')
                css_selector = '#' + identifier
            elif child.get('class'):
                identifier = child.get('class')[0]
                css_selector = '.' + identifier
            else:
                raise ValueError('The element does not have an id or a class')
        
            elemental = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        
        return elemental
    


    
    def fill_that_form(self):                                                                            #v For `select` when there's too many answers!!
        #if self.form_input_extended['mandatory'] is True and (self.form_input_extended['env_values'] or self.form_input_extended['env_html']):
        # ^ the purpose of the if is b/c...  if we don't need(['mandatory']) to do the question then we don't!!!!
        print("fill_that_form()")
        if self.form_input_extended['env_key'] and self.form_input_extended['env_values']:
            #print("fill_that_form()")
            print('\n\n')
            print(self.form_input_extended)
            print('\n\n')
            time.sleep(1)
            
            
            
            
            
            
            
            element = self.form_input_extended['env_html']
            value = self.form_input_extended['env_values'][0]
            print("element = ", element)
            print("value = ", value)
            success = self.troubleshoot_form_filling(element, value)
            if not success:
                print("Failed to fill in the form. See the error messages above for details.")
            else:
                print("Successfully filled in the form.")
            #-------------------------------------------------------------------------------------------
            #This  v  checks if the "value" is 'empty' or 'None'
            #if self.form_input_extended['bc_nick_said']:
            if 'bc_nick_said' in self.form_input_extended:
                if self.form_input_extended['bc_nick_said'] == True:
                    pass
                elif self.form_input_extended['bc_nick_said'] == False:
                    print("Release the hounds Mr. Smithers...")
                    #self.form_input_extended['bc_nick_said'] == False
                    return
            
            
            
            
            
            
            
            
            # if self.form_input_extended['env_key'] == 'PHONE_NUMBER':
            #     print("Ok at least I made it in here!")
            #     element = self.form_input_extended['env_html']
            #     value = self.form_input_extended['env_values'][0]
            #     print("element = ", element)
            #     print("value = ", value)
                
            #     success = self.troubleshoot_form_filling(element, value)
                
            #     if not success:
            #         print("Failed to fill in the form. See the error messages above for details.")
            #     else:
            #         print("Successfully filled in the form.")
            
            
            
            
            
            
            
            
            
            
            
            if self.form_input_extended['text'] is True:
                #for form_input_answer in self.form_input_extended['env_values']:
                #form_input_answer = self.form_input_extended['env_values']
                print("MADE IT INTO [TEXT] - MADE IT INTO [TEXT] - MADE IT INTO [TEXT] - MADE IT INTO [TEXT]")
                for form_input_ans in self.form_input_extended['env_values']:
                    print("form_input_ans = ", form_input_ans)
                    form_input_answer = form_input_ans
                form_input_html = self.form_input_extended['env_html']
                
                if form_input_answer:
                    #form_input_html.click()
                    #self.browser.form_input_html.send_keys(form_input_answer)
                    #self.form_input_html.send_keys(form_input_answer)
                    form_input_html.send_keys(form_input_answer)
                    print("Text should be inserted => ", form_input_answer)
                    time.sleep(3)
                    return
                
                        
            elif self.form_input_extended['select'] is True:
                #form_input_answer = self.form_input_extended['env_values']
                for form_input_ans in self.form_input_extended['env_values']:
                    print("form_input_ans = ", form_input_ans)
                    form_input_answer = form_input_ans
                
                if answer:
                    form_input_html = self.form_input_extended['env_html']
                    input_select_element = self.form_input_html.find_element(By.TAG_NAME, "input")
                    #select_button = self.form_input_extended(By.)

                    input_select_element.click()
                    answer = form_input_html.find_element(By.ID, form_input_answer)
                    answer.click()
                    return
                elif form_input_answer is None:
                    form_input_html = self.form_input_extended['env_html']
                    input_select_element = self.form_input_html.find_element(By.TAG_NAME, "input")
                    
                    input_select_element.click()
                    self.input_select_element.send_keys(By.TEXT, form_input_answer)
                    self.send_keys("ENTER")
                    if input_select_element == form_input_answer:
                        return
                    elif input_select_element is None:
                        print("Try pressing the `down-arrow` key and then click `ENTER`!!")
                        print("Otherwise click the correct school!")
                    elif input_select_element is not form_input_answer:
                        raise BreakLoopException
                        
            if self.form_input_extended['radio'] is True:
                form_input_answer = self.form_input_extended['env_values']
                form_input_html = self.form_input_extended['env_html']
                
                answer = form_input_html.find_element(By.ID, form_input_answer)
                if answer:
                    answer.click()
                    return
                elif answer is None:
                    answer = self.browser.find_element(By.TEXT, form_input_answer)
                    if answer:
                        answer.click()
                    elif answer is None:
                        print("Ummmm I have no clue about this [radio] call the police maybe??")
                        
            if self.form_input_extended['checkbox'] is True:
                #TODO: Utilize the `select_all` || `select_one` from  self.form_input_extended['']
                form_input_answer = self.form_input_extended['env_values']
                form_input_html = self.form_input_extended['env_html']
                
                answer = form_input_html.find_element(By.ID, form_input_answer)
                if answer:
                    answer.click()
                    return
                elif answer is None:
                    answer = self.browser.find_element(By.TEXT, form_input_answer)
                    if answer:
                        answer.click()
                    elif answer is None:
                        print("Ummmm I have no clue about this [checkbox] call the police maybe??")
                        
            if self.form_input_extended['button'] is True:
                form_input_answer = self.form_input_extended['env_values']
                form_input_html = self.form_input_extended['env_html']
                
                answer = form_input_html.find_element(By.ID, form_input_answer)
                if answer:
                    answer.click()
                    return
                elif answer is None:
                    answer = self.browser.find_element(By.TEXT, form_input_answer)
                    if answer:
                        answer.click()
                    elif answer is None:
                        print("Ummmm I have no clue about this [checkbox] call the police maybe??")
                        
            elif self.form_input_extended['file'] is True:
                form_input_answer = self.form_input_extended['env_values']
                form_input_html = self.form_input_extended['env_html']
                
                answer = form_input_html.find_element(By.ID, form_input_answer)
                if answer:
                    answer.click()
                    return
                elif answer is None:
                    answer = self.browser.find_element(By.TEXT, form_input_answer)
                    if answer:
                        answer.click()
                    elif answer is None:
                        print("Ummmm I have no clue about this [file] call the police maybe??")
                        
        if self.form_input_extended['mandatory'] is True and not self.form_input_extended['env_values']:
            if self.max_similarity < .25:
                print("prompt user to answer!!!")
            else:
                #Skips the form
                raise BreakLoopException
    
    def troubleshoot_form_filling(self, element, value):
        try:
            # Check if the value is not None or empty
            if not value:
                print("Error: Value is None or empty")
                return False

            # Check if the element is present
            if element is None:
                print("Error: Element is None")
                return False

            # Check if the element is an input field
            if element.tag_name.lower() != 'input':
                print(f"Error: Element is not an input field, it's a {element.tag_name}")
                return False

            # Check if the element has the correct attributes
            if element.get_attribute('name') != 'job_application[phone]':
                print("Error: Element has incorrect name attribute")
                return False

            # Check if the element is displayed (visible to the user)
            if not element.is_displayed():
                print("Error: Element is not displayed")
                return False

            # Check if the element is enabled (interactable)
            if not element.is_enabled():
                print("Error: Element is not enabled")
                return False

            # Try to fill in the form
            element.clear()
            element.send_keys(value)
            print(f"Success: Filled in the form with {value}")

            return True
        except Exception as e:
            print(f"Error: An exception occurred: {e}")
            return False

    
    #*Scrolls to each question in the form
    def scroll_to_question(self, input_data_html):
        print("\nscroll_to_question()")
        soup = BeautifulSoup(input_data_html, 'lxml')
        print("soup = ", soup)
        
        body_children = soup.body.contents
        for child in body_children:
            print('element = ', child)
            
            if child.get('id'):
                identifier = child.get('id')
                css_selector = '#' + identifier
            elif child.get('class'):
                identifier = child.get('class')[0]
                css_selector = '.' + identifier
            else:
                raise ValueError('The element does not have an id or a class')
        
            elemental = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        
            self.browser.execute_script("arguments[0].scrollIntoView();", elemental)
    
    # def form_fields_requirement(self, form_input_answers, label):
    #     #TODO: Make sure to remove the % %
    #     NA_option = True if "Not Applicable" in label or "N/A" in label else False
    #     #TODO: Make sure to remove the | |
    #     SELECT_ONE = True if "select one" in label else False
    #     SELECT_ALL = True if "select all" in label or "N/A" in label else False
    #     MARK_ALL = True if "select all" in label else False
        

        
        
    #     if "*" in label or "✱" in label:
    #         #look through .env for a matching key
    #             #if match_found -> look at key's value
    #                 #if value wrapped in between %% remove them
    #                 #elif value wrapped in between || remove them
    #                 #else return value
    #             #else
        
    #     if "Not Applicable" in label or 'N/A' in label:
    #         #look through .env for a matching key
    #             #if match_found -> look at key's value
    #                 #if value wrapped in between %% user prefers N/A
    #                 #elif value wrapped in between || user prefers 'skip question'
    #                 #else return value
    #             #else
                
    # def job_type_preferences(self, requested_job_type):
        
            
    #TODO: Make the weight of 'your' and 'user'/'users' EQUAL (What is you address? = USERS_ADRESS)!!!!!!
    #TODO: For 'I acknowledge' buttons check the answers for that and just skip everything!!
        #TODO: Same with 'subscribe' && '?'
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!                               TESTING                                         ! [https://github.com/explosion/spaCy]
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    def init_form_input_extended(self):
        self.form_input_extended = {
            "mandatory": False,
            "text": False,
            "select": False,
            "radio": False,
            "checkbox": False,
            "button": False,
            "file": False,
            "select all": False,
            "select one": False,
            "dynamic": False,
            "env_key": None,
            "env_values": [],
            "env_html": None
        }
    
    #*Analyzes the label and values along with the .env(key-value) && config.py files
    #! THIS METHOD IS WHERE WE FIND OUT IF WE HAVE AN ANSWER OR NOT!!    ssoooo if we don't then we send fill_in_form() that user_response is needed!!!
    #TODO: Make sure sure to handle N/A situations as well!!
    #! THIS SHOULDN'T HAVE return ANYWHERE OTHER THAN THE END!! This should only basically be re-directs!!!!
    def process_form_inputs(self, form_input_details):
        print("\nprocess_form_inputs()")
        self.init_form_input_extended()
        
        # self.nlp_load()
        # print("nlp loaded... ")
        
        #print("self.form_input_details: ", end="")
        #print(self.form_input_details)
        #print("form_input_details: ", form_input_details)
        submit_button = None
        remove_attachment = None
        resume_attachment = None
        for i, input_data in enumerate(form_input_details):
            try:
                print("\n\n\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
                
                time.sleep(2)
                self.init_form_input_extended()
                self.is_special_case(input_data)
                
                #++++++++++++++++++++++++++++++ MAYBE treat like edge cases +++++++++++++++++++++++++++++++++++++++
                print("Input " + str(i) + ":")
                print("  form_input_details = ", input_data)
                if input_data['is_hidden']:
                    continue
                
                
                
                #|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
                #       iMac Computer needed this for testing!!!
                # if i == [1, 2, 3, 4, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]:
                #     self.form_input_extended['bc_nick_said'] == True
                #|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
                
                
                
                
                # print("This is -> is None")         |       print("This is -> == None")         =>       print("This is -> None or empty")
                # if input_data['label'] is None:     |       if input_data['label'] == None:     =>       if not input_data['label']:
                #     print("Dang so -> is None")     |           print("Dang so -> == None")     =>           print("Dang so -> is None or empty")
                #     continue                        |           continue                        =>           continue
                
                
                #! THIS HAS TO BE 1st!!!!!!!!!  b/c if it's None or 'empty'(null) then all the other tests give erros when comparring!!
                print("This is -> None or empty")
                #Basically checks for None and empty!!
                if not input_data['label'] or input_data['label'] == None:
                    print("Dang so -> is None or empty")
                    continue
                
                print("This is -> dynamic")
                # or input_data['label'] is None:
                if 'dynamic' in input_data['label']:
                    print("Dang so -> dynamic")
                    continue
                
                print("This is -> == None       ...straight-up")
                if input_data['label'] is None:
                    print("Dang so -> == None       ...straight-up")
                    continue
                
                print("This is -> == None       IT'S A STRING")
                if input_data['label'] == 'None':
                    print("Dang so -> == None       IT'S A STRING")
                    continue
                
                
                
                if 'Remove attachment' in input_data['label']:
                    print("Remove attachment: (a file of sorts)")
                    print("input_data: ", input_data)
                    remove_attachment = input_data
                    print("remove_attachment: ", remove_attachment)
                    continue
                
                
                if 'Resume/CV' in input_data['label']:
                    print("Resume/CV: (a file)")
                    print("input_data: ", input_data)
                    resume_attachment = input_data
                    print("resume_attachment: ", resume_attachment)
                    continue
                

                if 'Submit Application' in input_data['label']:
                    print("Submit Application")
                    print("input_data: ", input_data)
                    submit_button = input_data
                    print("submit_button: ", submit_button)
                    continue
                #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                
                
                self.scroll_to_question(input_data['html'])
                #self.scroll_to_element(input_data)
                print("  Scrolled here I guess...\n")
                print("self.form_input_extended = ", self.form_input_extended)
                time.sleep(3)
                
                label = input_data['label']
                print("unprocessed label: ", label)
                label = self.process_text(label)
                print("processed label: ", label)
                input_type = input_data['type']
                predefined_options = input_data.get('values', None)
                print("predefined_options = ", predefined_options)
                
                # If the input type in select, radio, or checkbox, handle it as a !special case!
                print("\n_____________________________________________________________________________________")
                print("TIME FOR COMPARISONS! DO YOU HEAR THAT BUTT-HEAD!!! WE ARE GONNA BE COMPARING BUTTS!!")
                if input_type in ['select', 'radio', 'checkbox']:
                    print("Ahhhhhhh yes a very sexual we have come across as it is either one of these: 'select', 'radio', 'checkbox'")
                    matching_keys = self.get_matching_keys(label)               #! .get_matching_keys() does all the comaparing to get the right answer!!!!! ssooo there do   special case check -> .env chack -> long q>a ... a>a check!!!
                    if matching_keys:
                        #!HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE
                        print("self.form_input_extended = ", self.form_input_extended)
                        for key in matching_keys:
                            
                            answer = self.users_information[{key}]
                            print("answer = ", answer)
                            if answer in predefined_options:
                                # Input the answer into the form
                                print(f"Entering '{answer}' for '{label}'")
                            else:
                                print(f"Stored answer '{answer}' is not a valid option for '{label}'")
                    else:
                        print(f"No stored answers found for '{label}'")
                        
                else:
                    print("This one ain't special... this one ain't even intelligent... dumb ol' question any how")
                    matching_keys = self.try_finding_match(label)
                    print("matching_keys = ", matching_keys)
                    #! MAYBE HERE MAYBE HERE MAYBE MAYBE HERE MAYBE HERE MAYBE HERE
                    #self.form_input_extended['env_key'] = key
                    #self.form_input_extended['env_values'].append(self.users_information[key])
                    print("if matching_keys: ", end="")
                    print("True" if matching_keys else "False")
                    # if matching_keys:
                    #     for key in matching_keys:
                    if matching_keys:
                        print("self.form_input_extended['env_values'] = ", self.form_input_extended['env_values'])
                        for key in self.form_input_extended['env_values']:
                            print("key = ", key)
                            answer = self.users_information.get(key)
                            print("answer = ", answer)
                            # Input the answer into the form
                            print(f"Entering '{answer}' for '{label}'")
                            #self.fill_form(label, answer)
                    else:
                        context = self.q_and_a['summary'] + " " + label
                        answer = self.generate_response(context)
                        if answer:
                            # Input the answer into the form
                            print(f"Entering '{answer}' for '{label}'")
                            #self.fill_form(label, answer)
                        else:
                            print(f"No stored answers found for '{label}'")
                self.form_input_extended['env_html'] = self.extract_css(input_data['html'])
                
                self.print_form_input_extended()     ############################### HERE VON!!!
                
                self.fill_that_form()
                            
                            
            except BreakLoopException:
                print("You know what eff that job anyways! They probably suck and would've over worked you anyways.")
                return
            
            
        self.submit_job_application(submit_button)
        print("ALL DONE!!! The job application has been completed Reverand Mackie...")
        print("Normally Germans would push the 'Submit Application' button right now!")
        time.sleep(20)
    
    
    def try_finding_match(self, label):
        print("\n1)try_finding_match()")
        words_in_label = label.split()
        jacc_key = None
        if len(words_in_label) <= 2:
            print("This question has 2 words or less.")
            print(words_in_label)
        
        else:
            print("This question has more than 2 words.")
            #! => doc = self.nlp(label)
            named_entities, headword, dependants = self.spacy_extract_key_info(self.nlp(label))
            print(f"named_entities = {named_entities}")
            print(f"headword = {headword}")
            print(f"dependants = {dependants}")
            key = self.generate_key(named_entities, headword, dependants)
            jacc_key = key.lower().replace("_", " ")
            print("jacc_key = ", jacc_key)
        
        #self.JobSearchWorkflow_instance.load_custom_rules()
        print("words_in_label = ", words_in_label)
        print("label = ", label)
        #NOTE: Remember Q_AND_A is only for the summary! So we only traverse CUSTOM_RULES!!
        print("self.custom_rules = ", self.custom_rules)
        #? These might work in case that one doesn't
        #for rule in self.custom_rules.keys():
        #for rule, value in self.custom_rules.items():
        #for rule, value in self.custom_rules:
        for rule in self.custom_rules:
            if label == rule:
                print("MATCH: [ try_finding_match() ]")
                print("\tCUSTOM_RULES = ", rule)
                print("\tlabel = ", label)
                #print("\t... value = ", value)
                print("\t... value = ", self.custom_rules[rule])
                return rule
            
        found_best_match = self.find_best_match(label)
        print("found_best_match = ", found_best_match)
        
        #TODO: REPLACE THIS    v!!!!!!!!!!
        # if label == config.py[key]:
        #     return config.py[key]
        if found_best_match:
            return found_best_match
        #! RECENT CHANGE RECENT CHANGE RECENT CHANGE
        # elif self.jaccard_similarity(jacc_key, label):
        #     return jacc_key
        # else:
        #     #Since `rule` was previously defined you use it as above but since `summary` wasn't {something about Python treats} so just use () with '' inside it and the variable name within the ''
        #     return self.generate_response(self.q_and_a('summary'))
       
        
        #! HERE HERE HERE HERE
               
                   
        else:
            jacc_key
    
    
    #*SpaCy's needs and dumb stuff gone
    #TODO: do something with the dumb *!!!!
    def process_text(self, text):
        print("process_text()")
        if "*" in text or "✱" in text:
            self.form_input_extended['mandatory'] = True
        if 'select one' in text.lower():
            self.form_input_extended['select one'] = True
        if 'select all' in text.lower() or 'mark all' in text.lower():
            self.form_input_extended['select all'] = True
        return text.lower().strip().replace("(", "").replace(")", "").replace(".", "").replace("?", "").replace("*", "").replace("✱", "").strip()
    
    #*Answer simple question for user based off their provided summary
    def generate_response(self, context):
        print("\ngenerate_response()")
        print("context = ", context)
        input_ids = self.tokenizer.encode(context, return_tensors='pt').to("cuda" if torch.cuda.is_available() else "cpu")

        max_length = len(input_ids[0]) + 100
        output = self.model.generate(input_ids, max_length=max_length, temperature=0.7)
        response = self.tokenizer.decode(output[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
        print("response = ", response)
        
        return response
    
    #*Checklist/Radio just transitions Yes-True && No-False
    def bool_to_str(self, value):
        print("\nbool_to_str()")
        return "Yes" if value.lower() == "true" else "No"
    
    #*SpaCy runs SpaCy methods
    def spacy_extract_key_info(self, doc):
        print("\nspacy_extract_key_info()")
        print("\n\n--------------------------------------------------------")
        print("My Way")
        print("spacy_extract_headword_and_dependants()")
        headword = ""
        dependants = []
        for token in doc:
            print(f"""
                  TOKEN: {token.text}
                  ====
                  {token.tag_ = }
                  {token.head.text = }
                  {token.dep_ = }
                  """)
            
            
            print(token.head)
            if token.dep_ == "ROOT":
                headword = token.head.text
            elif token.dep_ in {"compound", "amod", "attr"}:
                dependants.append(token.lemma_)
                #dependants.append(token.text)
        print(f"headword = {headword}")
        print(f"dependants = {dependants}")
        #return headword, dependants
        print("--------------------------------------------------------")
        
        print("\n\n--------------------------------------------------------")
        print("Their Dumb Way")
        named_entities = [ent.text for ent in doc.ents]
        headword = ""
        dependants = []
        for token in doc:
            if token.dep_ == "ROOT":
                headword = token.lemma_
            elif token.dep_ in {"compound", "amod", "attr"}:
                dependants.append(token.lemma_)
        print(f"named_entities = {named_entities}")
        print(f"headword = {headword}")
        print(f"dependants = {dependants}")
        #return named_entities, headword, dependants
        print("--------------------------------------------------------")
        return named_entities, headword, dependants
    
    #*If SpaCy special case needs to be made... ensure it!! and if still yes then do so here
    def generate_key(self, named_entities, headword, dependants):
        print("\ngenerate_key()")
        # Using set automatically eliminates duplicates for us!!
        tokens = set(named_entities + [headword] + dependants)
        key = "_".join(tokens).upper()
        print(f"key = {key}")
        return key
    
    #TODO: ADD NEW key-value PAIR TO FILE  &&  THE custom_rules or users_information
    #*Add !UNIQUE! key-value pair to EITHER config.py || .env
    def store_new_answer(self, question, answer):
        print("\nstore_new_answer()")
        #nlp = spacy.load("en_core_web_md")
        doc = self.nlp(question.lower())
        named_entities, headword, dependants = self.spacy_extract_key_info(doc)
        key = self.generate_key(named_entities, headword, dependants)
        #key = self.verify_key(key, question)
        
        # If key is unique, add it to the .env file
        if key not in self.users_information:
            self.users_information[key] = answer
            with open(self.env_path, "a") as file:
                file.write(f"\n{key}='{answer}")
    
    #*Uses label to try and find a matching key from the users' .env
    def find_best_match(self, label):
        print("\n2)find_best_match()")
        
        doc1 = self.nlp(label.lower())
        print("-doc1 = ", doc1)
        max_similarity = -1
        best_match = None
        synonyms = self.get_synonyms(label)
        
        print("users_information + 1")
        for key in self.users_information.keys():
            doc2 = self.nlp(key.lower().replace("_", " "))
            print("-doc2(self.users_information.key) = ", doc2)
            similarity = doc1.similarity(doc2)
            print("similarity = ", similarity)
            print("key = ", key)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = key    #leave as = to key so it's just easier for later!!
                print("max_similarity = ", max_similarity)
                print("best_match = ", best_match)
                
                if max_similarity == 1.0:
                    print("Before assignment:", self.form_input_extended)
                    print("Before assignment(key):", key)
                    self.form_input_extended['env_key'] = key
                    print("After assignment:", self.form_input_extended)
                    print("After assignment(key):", key)
                    
                    self.form_input_extended['env_values'].append(self.users_information[key])
                    print("MATCH: [ 2.1)find_best_match() -> .similarity(question{*label*} | self.users_information.key)]")
                    print("\tusers_information = ", key)
                    print("\tlabel = ", label)
                    print("\t... value = ", self.users_information[key])
                    #print("\t... value = ", self.users_information['{key}'])
                    return key
                elif len(synonyms) > 0:
                    for synonym in synonyms:
                        doc2_syn = self.nlp(synonym.lower().replace("_", " "))
                        similarity_syn = doc2_syn.similarity(doc2)
                        if similarity_syn > max_similarity:
                            max_similarity = similarity_syn
                            best_match = key
                            
                            if max_similarity == 1.0:
                                print("Before assignment:", self.form_input_extended)
                                print("Before assignment(key):", key)
                                self.form_input_extended['env_key'] = key
                                print("After assignment:", self.form_input_extended)
                                print("After assignment(key):", key)
                                
                                self.form_input_extended['env_values'].append(self.users_information[key])
                                print("MATCH: [ 2.1)find_best_match() -> .similarity(question{*label*} | self.users_information.key)]")
                                print("\tusers_information = ", key)
                                print("\tlabel = ", label)
                                print("\t... value = ", self.users_information[key])
                                #print("\t... value = ", self.users_information['{key}'])
                                return key
                
                
            # Check for synonyms
            #! WRONG ! sometimes I have 2 so get the root or something!!!
            #synonyms = self.get_synonyms(key)
            #synonyms = self.get_synonyms(label)
            
            
            #!-------------------------------------------------------------------------------------------------------------------------
            # for synonym in synonyms:
            #     doc2 = self.nlp(synonym.lower().replace("_", " "))
            #     print("-doc2(synonyms.index) = ", doc2)
            #     #similarity = doc1.similarity(doc2)
            #     similarity = doc2.similarity(doc1)
            #     print("similarity = ", similarity)
            #     print("key = ", key)
            #     print("synonyms = ", synonyms)
            #     if similarity > max_similarity:
            #         max_similarity = similarity
            #         best_match = key
            #         print("max_similarity = ", max_similarity)
            #         print("best_match = ", best_match)
                    
            #         if max_similarity == 1.0:
            #             self.form_input_extended['env_key'] = key
            #             self.form_input_extended['env_values'].append(self.users_information[key])
            #             print("MATCH: [ 2.2)find_best_match() -> .similarity(question{*label*} | synonyms.index)]")
            #             print("\tusers_information = ", key)
            #             print("\tlabel = ", label)
            #             print("\t... synonym = ", synonym)
            #             print("\t... value = ", self.users_information[key])
            #             #print("\t... value = ", self.users_information['{key}'])
            #             return key
            #!-------------------------------------------------------------------------------------------------------------------------
            
            
            print("\nusers_information + 1")
            
        print("max_similarity = ", max_similarity)
        print("best_match = ", best_match)
        print(best_match if max_similarity > 0.90 else None)
        return best_match if max_similarity > 0.90 else None
    
    #*This is the DOUBLE CHECK
    def get_synonyms(self, word):
        print("\n3)get_synonyms()")
        print(f"word = {word}")
        #TODO: Ensure this resets the list of synonyms each time
        synonyms = []

        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())
        #TODO: DOUBLE CHECK THIS!!!!! Your asking for the synonyms of `phone number`?!?!?!?! Do we really want the synonyms for the key and not the label?!?!?!
        if word.lower() in self.custom_synonyms:
            #for custom_syn in self.custom_synonyms[word]:
            for custom_syn in self.custom_synonyms[self.process_text(word)]:
                #synonyms.extend(custom_syn)
                print("filtered_custom_syn = ", end="")
                filtered_custom_syn = self.process_text(custom_syn)
                filtered_custom_syn = filtered_custom_syn.replace("_", " ")
                print(filtered_custom_syn)
                synonyms.append(filtered_custom_syn)

        print("self.custom_synonyms = ", end="")
        print(self.custom_synonyms)
        
        
        print("synonyms = ", end="")
        print(synonyms)
        print("\n--------------------")
        
        time.sleep(2)
        
        return synonyms
    
    #*Just for me to see what it does!! Crapola looks haaatt!
    def jaccard_similarity(self, sentence1, sentence2):
        print("\njaccard_similarity()")
        set1 = set(sentence1.lower().split())
        set2 = set(sentence2.lower().split())
        intersection = set1.intersection(set2)
        print(f"intersection = {intersection}")
        union = set1.union(set2)
        print(f"union = {union}")
        jaccard_similarity = (len(intersection) / len(union))
        print(f"jaccard_similarity = {jaccard_similarity}")
        if jaccard_similarity > 90:
            return True
        else:
            return False
    
    def submit_job_application(self, submit_button):
        
        print("We are about to click the submit button")
        time.sleep(3)
        submit_button = self.extract_css(submit_button['HTML'])
        print("submit_button = ", submit_button)
        time.sleep(1)
        submit_element_idk = self.browser.find_element(By.CSS_SELECTOR, submit_button)
        print("submit_element_idk = ", submit_element_idk)
        time.sleep(1)
        self.keep_jobs_applied_to_info()
        self.sessions_applied_to_info
        return
        
        
        
        
        
        #submit_button_index = self.form_input_details.get('KEY-NAME')
        #submit_button = self.extract_css(submit_button_index['HTML'])
        
        submit_button = self.extract_css(submit_button['HTML'])
        
        self.browser.find_element(By.CSS_SELECTOR, submit_button).click()
        
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".response-message")))
        
        response_message = self.browser.find_element(By.CSS_SELECTOR, ".response-message").text
        if "success" in response_message.lower():
            self.keep_jobs_applied_to_info()
            print("Form submission was successful!")
        else:
            print("Form submission failed!")
            
        error_messages = self.driver.find_elements(By.CSS_SELECTOR, ".error-message")
        for error_message in error_messages:
            print(f"Error: {error_message.text}")
            
        #TODO: Add call to oxylabs captcha!!!!!
            
        #TODO: I believe I just return all the way to go to the next job application!!!!
        #return

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!                                                                               !
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    #TODO: Check the wording in the question
    #*special_case() method 2
    def is_special_case(self, input_data):
        label = input_data['type']
        if label in ['select', 'radio', 'checkbox', 'file']:  #NOT 'button' b/c that's just the Submit
            if label == 'select':
                select_element = self.browser.find_element(label)
                is_multiple_choice = select_element.get_attribute('multiple') is not None
                if is_multiple_choice is True:
                    self.form_input_extended['text'] = 'is_multiple_choice'
                elif is_multiple_choice is False:
                    pass
            elif label == 'checkbox':
                self.form_input_extended['checkbox'] = True
                self.form_input_extended = 'is_multiple_choice'
            elif label == 'radio':
                self.form_input_extended['radio'] = True
            elif label == 'file':
                self.form_input_extended['file'] = True
        else:
            if label == 'text' or label == 'textarea':
                self.form_input_extended['text'] = True
            elif label == 'button':
                self.form_input_extended['text'] = True
            
            else:
                print("There has been an error father...")
                print("label = ", label)
        return
    
    
    
    
    
    #TODO: Once we submit the application confirm that here and then save everything!!!
        #? For the user or my google_sheet_stats i don't know???
    #* My vote is we leave it as it is so b/c this is the correct format for Google Sheet's!!!
    #* Then JobsThatUserHasAppliedTo.csv has the same format and we can just add the session time at the end easily!!
    #! REMEMBER: if the program crashes it has to hold/preserve values!!!
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def keep_jobs_applied_to_info(self):
        self.sessions_applied_to_info.append({
            'Job_URL': self.current_url,
            'Company_Name': self.company_name,
            'Job_Title': self.company_job_title,
            'Company_Job_Location': self.company_job_location,
            'Company_Department': self.company_job_department,
            'Job_ID_Number': self.job_id_number,
        })
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!




    def keep_jobs_applied_to_info(self):
        self.jobs_applied_to_this_session.append(self.current_jobs_details)








class BreakLoopException(Exception):
    pass




  
    
    
    
    
    #FILTER OUT: Two (2) years of hands-on experience writing professional software code.
    #BIRTHDAY: Calculate their age using YYYY
    
    
    #NOTE: q_considerations -> 
        # https://boards.greenhouse.io/affirm/jobs/5600147003 -> checklist's say (select one)
        
    
    
    
    #dictionary variable = {
    #     question: 'How fat was the biggest wave ever surfed? (select one)'
    #     q_considerations: ''
    # }
    
    
    
    
    
    
    #ADD TO process_form_inputs()
            #     print("Looking for dynamic answers")
            # for predefined_answer in form_input_details.get('values'):
            #     if "(dynamic)" not in predefined_answer:
            #         #current index + 1   ->    is dynamic {SSSOOOOO if we pick that to be the answer THEN prepare & take special care of the next question}
            #         #answer_results_dynamic = predefined_answer          #Save the answer that will lead to a pop-up dynamic question
            #         self.form_input_extended['dynamic'] = True
                    
            # print("Looking for dynamic questions")
            # for j in reversed(range(i)):
            #     #label = form_input_details[j]['label']         #if the 'label' keys' value is empty this action will prompt a KeyError BUT...  using .get() won't!!!
            #     if input_data.get('label') == form_input_details[j].get('label'):
            #         #TODO:Figure out how to get access to the previous input ALSO  !ALSO! REMEMBER the questions in form_input_details are sometimes out of order
            #         self.form_input_extended['dynamic'] = True
            #         continue
            #     #!RECENT CHANGE sssoooooo if anything happens it's cause of this
            #     # else:
            #     #     if duplicate_label == current_label:
            #     #         has_dynamic_question = duplicate_label          #NOT current_label becuase THAT IS the duplicate and we're looking for the O.G., which is everything that came before it!!!!
            #     # OR OR OOOORRRRRRRR just as Chat-GPT did in fill_out_form() is any of these dynamic things are ran into handle them immediately and then just do `continue` so it skips it on the next iteration!!!!
            
    
    
    
    
   