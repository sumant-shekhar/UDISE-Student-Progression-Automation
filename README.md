# UDISE+ Student Progression & Data Entry Automation

🚀 **Automate student data management on the UDISE+ (SDMS) portal with ease.**

This repository contains Python scripts designed to automate the tedious tasks of student progression and profile updates on the official UDISE+ portal. Built using Selenium, these scripts handle batch processing, randomized data entry (where applicable), and provide robust error handling to ensure a smooth automation experience.

Recently, the codebase was refactored to strictly adhere to **SOLID principles** and Clean Code architecture, breaking down massive files into modular, single-responsibility components for extreme reliability and easy maintenance.

---

## 🏗️ Architecture & Modules

The codebase is split into modular components, meaning the execution logic is completely separated from the browser automation tools:

- **`progression.py`**: The **Main Runner** for the Student Progression Module.
- **`EP_GP_SP_PP.py`**: The **Main Runner** for the Comprehensive Profile Update.
- **`webdriver_utils.py`**: Shared utility class handling robust interactions, retries, and stale element recovery.
- **`logger_utils.py`**: Handles generating timestamped JSON logs per session and per student.
- **`scraper.py`**: Scrapes and interprets on-screen student data (Name, PEN, Class).
- **`step1_general_profile.py`**: Handles logic for the General Profile (GP) section.
- **`step2_enrolment_profile.py`**: Handles logic for the Enrolment Profile (EP) section.
- **`step3_facility_profile.py`**: Handles logic for the Facility/Other Details Profile (SP) section.
- **`step4_profile_preview.py`**: Handles finalizing the profile and navigating to the next student.

---

## 📋 Features

### 1. Student Progression (`progression.py`)
Automates the **Progression Module** to move students from one academic year to the next.
- **Batch Promotion:** Automatically selects "Promoted" for all students in a class.
- **Randomized Marks & Attendance:** Generates realistic marks (60–80%) and attendance days (200–220) to save time.
- **Schooling Status:** Intelligently handles "Same School" vs "Left School" status.
- **Section Assignment:** Automatically assigns students to Section A.
- **Error Recovery:** Stale-element protection and per-student error handling so one failure doesn't stop the whole batch.

### 2. Comprehensive Profile Update (`EP_GP_SP_PP.py`)
Automates the full student profile update including **General Profile (GP)**, **Enrolment Profile (EP)**, and **Facility Profile (SP/PP)**.
- **Smart Data Filling:** Fills mobile numbers, admission numbers, and blood groups if missing.
- **Stream-Specific Subjects:** Automatically selects subjects for Class 11/12 students based on their stream (Arts/Science).
- **Health Data:** Randomizes Height and Weight based on class-specific averages (Class 1–10).
- **Detailed Logging:** Generates a timestamped JSON log file for every session, tracking successes and failures.
- **Manual Overrides:** Designed to work alongside manual CAPTCHA solving and navigation.

---

## 🛠️ Prerequisites

Before running the scripts, ensure you have the following installed:

- **Python 3.x**
- **Google Chrome Browser**
- **Required Python Libraries:**
  ```bash
  pip install -r requirements.txt
  ```
  *(Or install manually: `pip install selenium webdriver-manager`)*

---

## 🚀 Simple Guide: How to Use

### 1. Configure Credentials
Before running either script, open `progression.py` or `EP_GP_SP_PP.py` in your text editor and update the `USERNAME` and `PASSWORD` constants at the top of the files with your UDISE credentials.

### 2. Running Student Progression
When you want to **promote** students to the next class:
1. Run the script from your terminal:
   ```bash
   python progression.py
   ```
2. The Chrome browser will open and fill your credentials automatically.
3. Solve the **CAPTCHA** manually within the browser (you have 15 seconds).
4. Wait for the script to navigate, or manually navigate to the **Progression Module**.
5. Select your Class and Section, then click **Go**.
6. The script will automatically detect the loaded students and begin processing the list!

### 3. Running Profile Updates (GP/EP/SP)
When you want to **complete student profiles** (contact info, height/weight, subjects):
1. Run the script from your terminal:
   ```bash
   python EP_GP_SP_PP.py
   ```
2. Solve the **CAPTCHA** manually within the browser (you have 15 seconds).
3. The script will wait 25 seconds for you. Manually navigate to the **Student List** and click on the **Edit** icon for the *first* student you want to process.
4. Once the student's profile page loads, the script takes over. It will fill all sections (General, Enrolment, Facility), save them, and click "Next Student" to loop until the entire class is complete.

---

## 📊 Logging
The `EP_GP_SP_PP.py` script creates a JSON log file (e.g., `2026-05-15_22-12-03.json`) in the project directory. This log includes:
- Student identity (Name, PEN, Class).
- Updates performed (Phone, Admission No, Height/Weight).
- Success/Failure status and error messages.

---

## ⚠️ Disclaimer
**This tool is for educational purposes and to assist school administrators with data entry tasks.** 
- Ensure you have the authority to update the data you are processing.
- The developers are not responsible for any data inaccuracies or portal access issues resulting from the use of these scripts.
- Use responsibly and monitor the automation process.

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/sumant-shekhar/UDISE-Student-Progression-Automation/issues).

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
