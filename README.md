# UDISE+ Student Progression & Data Entry Automation

🚀 **Automate student data management on the UDISE+ (SDMS) portal with ease.**

This repository contains Python scripts designed to automate the tedious tasks of student progression and profile updates on the official UDISE+ portal. Built using Selenium, these scripts handle batch processing, randomized data entry (where applicable), and provide robust error handling to ensure a smooth automation experience.

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
  pip install selenium webdriver-manager
  ```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/sumant-shekhar/UDISE-Student-Progression-Automation.git
cd UDISE-Student-Progression-Automation
```

### 2. Configure Credentials
Open `progression.py` and `EP_GP_SP_PP.py` in a text editor and update the `USERNAME` and `PASSWORD` variables:
```python
USERNAME = "YOUR_UDISE_ID"
PASSWORD = "YOUR_PASSWORD"
```

### 3. Run the Scripts

#### For Student Progression:
1. Run the script:
   ```bash
   python progression.py
   ```
2. The browser will open. Solve the **CAPTCHA** manually.
3. Wait for the script to navigate or navigate manually to the **Progression Module**.
4. Select the Class and Section, then click **Go**.
5. The script will automatically start updating each student in the list.

#### For Profile Updates (GP/EP/SP):
1. Run the script:
   ```bash
   python EP_GP_SP_PP.py
   ```
2. Solve the **CAPTCHA** within 15 seconds.
3. Navigate manually to the **Student List** and click on the **Edit** icon for the first student you want to process.
4. The script will take over and process students one by one until the end of the list.

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
