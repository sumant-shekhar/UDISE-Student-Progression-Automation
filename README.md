# UDISE+ Student Progression Automation

This script is designed to automate the repetitive task of updating student progression data on the UDISE+ SDMS portal. It handles the entry of promotion status, marks, attendance, and schooling status for entire batches of students, significantly reducing manual data entry time.

## Overview

The automation performs the following actions in a continuous loop:
1. Detects all students listed in the current progression table.
2. Sets the promotion status to "Promoted (by Examination)".
3. Assigns a random percentage between 60% and 80%.
4. Assigns random attendance days between 200 and 220.
5. Determines schooling status based on available dropdown options (Same School or Left School with TC).
6. Sets the section to "A".
7. Submits the data and confirms the success dialog for each student.
8. Logs all activity to a timestamped JSON file for record-keeping.

## Prerequisites

Before running the script, ensure your environment meets these requirements:
- Python 3.x installed.
- Google Chrome browser installed.
- Selenium library installed.
- WebDriver Manager library installed.

You can install the necessary dependencies using pip:
pip install selenium webdriver-manager

## Setup and Configuration

1. Credentials: Open the script and locate the Login section. Replace the placeholder username and password with your actual UDISE+ credentials.
2. Timing: The script includes several wait periods (time.sleep) to allow the website to load. You can adjust these if your internet connection is significantly faster or slower than average.

## Operational Workflow

1. Start the Script: Run the script from your terminal or IDE.
2. Login and CAPTCHA: The script will open Chrome and navigate to the login page. It will enter your credentials, but you must manually solve the CAPTCHA. There is a 15-second pause built in for this purpose.
3. Navigation: After logging in, you have 35 seconds to manually navigate to the Progression module and select the specific class and section you wish to process.
4. Automated Processing: Once the script detects student rows on the page, it will begin processing them one by one.
5. Batch Transition: After a full page of students is updated, the script will wait for 10 seconds. During this window, you can select a different class or section from the portal's dropdown menus. The script will then automatically detect the new list of students and start the process again.

## Data Logging

Every session creates a new JSON log file named with the current date and time. These files contain:
- Session start and finish times.
- Total count of students processed.
- Specific details for each row, including the schooling status assigned.

## Technical Notes

- The script uses a "stale-safe" mechanism to re-locate web elements if the page refreshes or updates dynamically, which helps prevent common automation crashes.
- It utilizes JavaScript execution for dropdown selection to ensure compatibility with the portal's Angular-based interface.
- To stop the automation, simply close the browser window or press Ctrl+C in your terminal.

## Disclaimer

This tool is intended for administrative efficiency. Users should ensure that the randomized data (marks and attendance) complies with their actual school records or modify the script to pull precise data from a local source if required. Always monitor the automation to ensure it is interacting correctly with the portal.
