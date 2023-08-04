import requests
import hashlib
# Module for signing my data
from .signature_helper import sign_data

class DataCollector:
    def __init__(self, jobs_applied_to_this_session, time_program_ran):
        # Initaliaze variables
        self.store_job_data_csv_relative_path = r'DataCollection/JobsThatUserHasAppliedTo.csv'
        self.time_program_ran = time_program_ran
        self.jobs_applied_to_this_session = jobs_applied_to_this_session
        
        
    def collect_job_data(self, user_id, job_details):
        # All matching job_title data
        pass
    
    def organize_data(self, data):
        # Yep
        pass
    
    def save_user_data(self, jobs_applied_to_this_session):
        # Save the data locally of jobs the user applied to!!
        pass
    
    def retrieve_jobs_user_applied_to(self):
        with open(self.store_job_data_csv_relative_path) as jobs_user_applied_to_data:
            #TODO: v INCORRECT -> here just to look pretty!!
            self.organize_data(jobs_user_applied_to_data)