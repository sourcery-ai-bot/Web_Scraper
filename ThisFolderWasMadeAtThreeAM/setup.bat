@echo off

REM Create a virtual environment
python -m venv awesome_i_can_name_this_anything_i_told_google_my_organizations_name_was_Nicks_Private_Parts_and_that_i_sell_computer_parts

REM Activate the virtual environment
call awesome_i_can_name_this_anything_i_told_google_my_organizations_name_was_Nicks_Private_Parts_and_that_i_sell_computer_parts\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Run your Python script
python ..\Legit\JobSearchWorkflow.py

REM Deactivate the virtual environment
deactivate