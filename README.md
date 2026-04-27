# UDISE+ School Automation Suite

This repository contains two Python automation scripts that handle repetitive data entry on the **UDISE+ SDMS portal** (`sdms.udiseplus.gov.in`). Both scripts use Selenium to control a Chrome browser — they type, click, and fill forms exactly like a human would, just much faster and without mistakes.

---

## The Two Scripts at a Glance

| File | What it does | When to use it |
|------|-------------|----------------|
| `progression.py` | Fills the **Student Progression** table — marks, attendance, promotion status | End of academic year, when the school needs to submit progression data for each class |
| `EP_GP_SP_PP.py` | Fills **full student profiles** — General Profile, Enrolment Profile, Other Details, and submits Complete Data | When new or incomplete student profiles need to be filled in |

They are completely independent. You run whichever one is relevant to your task. They share the same design philosophy — same login flow, same stale-element safety, same JSON logging format.

---
---

# Script 1 — `progression.py`

## What It Does

Opens the Progression module on the UDISE+ portal and fills in the progression data row by row for every student visible on the page. After finishing one full page of students, it waits 10 seconds for you to switch to a different class, then automatically picks up the new list and processes those students too. It runs in an **infinite loop** until you manually stop it with `Ctrl+C`.

For every single student row it does this, in order:

1. **Promotion Status** → Sets dropdown to `Promoted (by Examination)`
2. **Marks in Percentage** → Types a random number between **60 and 80** into the marks field
3. **Days Attended** → Types a random number between **200 and 220** into the attendance field
4. **Schooling Status** → Reads what options are available in the dropdown:
   - If `Studying in Same School` is available → selects it
   - If it is NOT available (last class of the school) → falls back to `Left School with TC/without TC`
5. **Section** → Sets section to **A** (skips silently if the field is not found)
6. **Update button** → Clicks the Update button for that row
7. **Okay popup** → Dismisses the success confirmation popup

## How to Set It Up

Open `progression.py` and find these two lines near the top of the Login section:

```python
USERNAME = "paste_Your_username"
PASSWORD = "Paste_your_Password"


```

Replace `"username"` and `"Password"` with your actual UDISE+ login credentials. Save the file.

## How to Run It

```bash
python progression.py
```

### What happens step by step after you run it:

```
Step 1 — Chrome opens and goes to the login page
Step 2 — Username and password are typed automatically
Step 3 — Script pauses for 15 seconds
         YOU: solve the CAPTCHA manually in the browser
Step 4 — Login button is clicked automatically
Step 5 — Script pauses for 35 seconds
         YOU: navigate to the Progression module
              select the class and section you want to process
Step 6 — Script detects all student rows on screen and starts filling them
Step 7 — After finishing all rows, script waits 10 seconds
         YOU: (optional) switch to a different class/section
Step 8 — Script detects the new rows and processes them
         This repeats forever until you press Ctrl+C
```

## What It Prints to the Terminal

```
📄 Log file created: 2026-04-27_14-05-20.json
Login clicked! Waiting for dashboard...
🚀 Automation loop started. Script will continuously check for students...

Total students found: 18

── Row 1 ──
  ✅ Promoted(by Examination)
  ✅ Marks: 73%
  ✅ Days: 208
  ✅ Schooling Status: Same School
  ✅ Section: A
  ✅ Update clicked
  ✅ Okay clicked

── Row 2 ──
  ...

🎉 All students in this batch updated successfully!
📄 Log updated: /path/to/2026-04-27_14-05-20.json

⏳ Waiting 10 seconds for you to select and load the next class...
```

If no students are found on screen (e.g. you haven't selected a class yet):
```
👀 No students found on the page. Waiting 10 seconds for you to load a class...
```

If a stale element is encountered (Angular refreshes the page mid-action):
```
  ⚠️ Stale element, retrying (1/3)...
```

## What It Saves to the JSON Log

A new `.json` file is created in the same folder as the script every time you run it. The filename is the exact date and time the script started, for example `2026-04-27_14-05-20.json`.

**Top-level structure:**
```json
{
    "session": {
        "started_at": "2026-04-27T14:05:20.850068",
        "log_file": "2026-04-27_14-05-20.json",
        "username": "10140615303"
    },
    "summary": {
        "total_students": 34,
        "successful": 34,
        "failed": 0,
        "finished_at": "2026-04-27T14:45:10.123456"
    },
    "rows": [ ... ]
}
```

**Each row entry inside `"rows"`:**
```json
{
    "row_number": 1,
    "schooling_status": "Studying in Same School"
}
```

> Note: The log does **not** record marks or days for each row since those are random — only the schooling status is logged because it varies between classes.

---
---

# Script 2 — `EP_GP_SP_PP.py`

## What It Does

Opens a student's edit page and fills in their **complete profile** across four sections — General Profile, Enrolment Profile, Other Details/Facility Profile, and Profile Preview. After completing each student it checks whether there is a "Next Student" button or a "Back to School Dashboard" button. If there's a next student it clicks it and repeats. If it reaches the last student it clicks Back to Dashboard and **stops on its own** — no `Ctrl+C` needed.

### Section 1 — General Profile
- Reads the phone number currently saved. If it's blank, `9999999991`, or `9999999999` (placeholder values) → replaces it with a realistic random number starting with `97855`
- If the phone is already a real number → leaves it alone and skips
- Sets blood group to **O+** if not already set
- Saves and moves to the next tab

### Section 2 — Enrolment Profile
- Fills admission number with a random 2-digit number if the field is empty
- Sets Medium of Instruction to **Hindi** if not already set
- Selects Language Group — tries `English_Hindi_Sanskrit` first, falls back to `Hindi_English_Sanskrit`
- Clicks **NO** for the RTE Section 12C question
- Detects academic stream (Arts or Science) and selects the correct subject group from the multi-select dropdown
- Saves and moves to the next tab

### Section 3 — Other Details / Facility Profile
- Sets **Facilities provided: YES** and checks **Free TextBook**
- Answers **NO** to all of these questions: CWSN, SLD screening, ASD screening, ADHD screening, Gifted/Talented, Olympiads/NLC, NCC/NSS, Digital Devices capability
- Fills **Height and Weight** automatically using the student's class (read from the info card — no manual input needed). Values are randomized within a realistic range around the class average
- Sets distance from school to **1–3 km**
- Sets parent education level to **value 5**
- Saves and moves to the next tab

### Section 4 — Profile Preview and Complete Data
- Scrolls to the bottom of the preview page
- Clicks **Complete Data**
- Dismisses the confirmation popup
- Checks for **Next Student** or **Back to School Dashboard** to decide whether to continue or stop

## Height and Weight Logic

The script reads the class name directly from the student info card at the top of the page (e.g. `"II"`, `"UKG/KG2/PP1"`, `"VIII"`) and converts it to a number automatically. No manual input required.

```
"I"            → Class 1  → Height ~115 cm, Weight ~21 kg
"II"           → Class 2  → Height ~122 cm, Weight ~23 kg
"III"          → Class 3  → Height ~128 cm, Weight ~26 kg
"IV"           → Class 4  → Height ~133 cm, Weight ~29 kg
"V"            → Class 5  → Height ~138 cm, Weight ~32 kg
"VI"           → Class 6  → Height ~144 cm, Weight ~36 kg
"VII"          → Class 7  → Height ~149 cm, Weight ~40 kg
"VIII"         → Class 8  → Height ~156 cm, Weight ~45 kg
"IX"           → Class 9  → Height ~164 cm, Weight ~51 kg
"X"            → Class 10 → Height ~170 cm, Weight ~56 kg
"UKG/KG2/PP1"  → Class 1  → Height ~115 cm, Weight ~21 kg
```

Every student gets a slightly different value — height is ±5 cm and weight is -3 to +5 kg from the base — so the data doesn't look copy-pasted across the whole class.

## How to Set It Up

Open `EP_GP_SP_PP.py` and find these two lines near the very top:

```python
USERNAME = "10140615303"
PASSWORD = "58#wwhLG"
```

Replace the values with your actual UDISE+ credentials. That is the only thing you need to change before running.

## How to Run It

```bash
python EP_GP_SP_PP.py
```

### What happens step by step after you run it:

```
Step 1 — Log file is created immediately in the same folder as the script
Step 2 — Chrome opens and goes to the login page
Step 3 — Username and password are typed automatically
Step 4 — Script pauses for 15 seconds
         YOU: solve the CAPTCHA manually in the browser
Step 5 — Login button is clicked automatically
Step 6 — Script pauses for 25 seconds
         YOU: navigate to the first student's edit page
              make sure you are on the General Profile tab
Step 7 — Script reads the student info card at the top of the page
         (Name, Class, Section, Academic Year, PEN)
Step 8 — Script fills all four profile sections automatically
Step 9 — After Complete Data is submitted:
         → "Next Student" button found → clicks it → goes back to Step 7
         → "Back to School Dashboard" found → clicks it → script stops
```

## What It Prints to the Terminal

```
📄 Log file created: 2026-04-27_14-05-20.json
⏳ Waiting 15 seconds — please solve the CAPTCHA in the browser...
✅ Login clicked! Waiting for dashboard...
⏳ Waiting 25 seconds — please open the student edit page...

==================================================
  Processing Student #1
==================================================
  📋 SUNNY RAJ | Class: II | Section: A | PEN: 23405424633 | Year: 2026-27
  ✅ Phone number set: 9785547382
  ✅ Blood group set to O+
  ✅ General Profile saved
  ✅ Moved to Enrolment Profile tab
  ✅ Admission number filled: 47
  ✅ Medium of Instruction set to Hindi
  ✅ Language group: English_Hindi_Sanskrit
  ✅ RTE 12C: NO selected
  ℹ️ Academic stream value: 1
  ✅ Arts stream — selecting subjects...
    ✅ Subject selected: Geography
    ✅ Subject selected: History
    ✅ Subject selected: Economics
  ✅ Enrolment Profile saved
  ✅ Facility: YES + Free TextBook checked
  ✅ CWSN: No
  ✅ SLD screening: No
  ✅ ASD screening: No
  ✅ ADHD screening: No
  ✅ Gifted/Talented: No
  ✅ Olympiads/NLC: No
  ✅ NCC/NSS: No
  ✅ Digital devices: No
  ℹ️ Class detected: 'II' → mapped to class 2
  ✅ Height: 124 cm | Weight: 25 kg
  ✅ Distance from school: 1–3 km
  ✅ Parent education level set
  ✅ Facility/Other Profile saved
  ✅ Complete Data clicked
  ✅ Moved to next student

==================================================
  Processing Student #2
==================================================
  ...

  🏁 Last student reached — clicking Back To School Dashboard...
  ✅ Back To School Dashboard clicked!

🎉 All students processed!
✅ Successful : 23
❌ Failed     : 0
📄 Log saved  : /path/to/2026-04-27_14-05-20.json
```

**If a phone number is already valid and was left alone:**
```
  ℹ️ Phone already valid: 7547003485, skipping.
```

**If a student fails entirely:**
```
  ❌ Student #3 FAILED: Message: element not found ...
```

**If a stale element is hit and retried:**
```
  ⚠️ Stale element on click, retrying (1/3)...
```

**If the student info card at the top can't be read:**
```
  ⚠️ Could not read student info card: ...
```

## What It Saves to the JSON Log

Same filename format — named by the exact time the script started.

**Top-level structure:**
```json
{
    "session": {
        "started_at": "2026-04-27T14:05:20.850068",
        "log_file": "2026-04-27_14-05-20.json",
        "username": "10140615303",
        "login_clicked_at": "2026-04-27T14:05:49.040073"
    },
    "summary": {
        "total_students": 23,
        "successful": 23,
        "failed": 0,
        "finished_at": "2026-04-27T15:10:33.000000"
    },
    "students": [ ... ]
}
```

**Each student entry inside `"students"` when successful:**
```json
{
    "student_number": 1,
    "timestamp": "2026-04-27T14:06:14.040677",
    "status": "success",
    "name": "SUNNY RAJ",
    "class": "II",
    "section": "A",
    "academic_year": "2026-27",
    "pen": "23405424633",
    "phone": "9785547382",
    "admission_no": "47",
    "height": "124",
    "weight": "25",
    "is_last_student": false,
    "error": null
}
```

**When a student failed:**
```json
{
    "student_number": 2,
    "status": "failed",
    "name": "AATIF FIRDOSH",
    "class": "II",
    "pen": "23346631169",
    "phone": "7547003485",
    "admission_no": null,
    "height": null,
    "weight": null,
    "is_last_student": false,
    "error": "Message: element not interactable ..."
}
```

Fields that show `null` were not reached before the failure. This tells you exactly how far the script got on that student before it crashed. If `phone` is filled but `height` is null, the crash happened somewhere in Section 3.

---
---

# Prerequisites (Both Scripts)

### Software
- Python 3.8 or higher
- Google Chrome (any recent version)

### Python packages
```bash
pip install selenium webdriver-manager
```

`webdriver-manager` automatically downloads the correct ChromeDriver version to match your installed Chrome — you do not need to download anything manually.

---

# Stopping the Scripts

| Script | How it stops |
|--------|-------------|
| `progression.py` | Never stops on its own. Press `Ctrl+C` in the terminal when done, or close Chrome. |
| `EP_GP_SP_PP.py` | Stops itself when it reaches the last student. You can also press `Ctrl+C` or close Chrome at any time. |

---

# Understanding the Icons in the Terminal

| Icon | Meaning |
|------|---------|
| ✅ | Step completed successfully |
| ℹ️ | Informational — something was skipped or auto-detected |
| ⚠️ | Warning — something went wrong but the script kept going |
| ❌ | Error — a step failed |
| 📄 | Log file was created or updated |
| ⏳ | Script is waiting — you need to do something manually |
| 🏁 | Last student reached, about to stop |
| 🎉 | All done |
| 👀 | No students found yet, waiting for you to load a class |

---

# Common Problems and Fixes

**"No students found on the page" keeps printing in a loop**
You haven't navigated to the Progression table yet, or you haven't selected a class and section from the dropdown. Do that and the script will detect the rows on its own.

**Student keeps failing with a long stacktrace in the error field**
The portal likely logged you out or had a timeout. Stop the script with `Ctrl+C`, log back in manually, navigate back to the student where it left off (check the JSON log for the last successful student number), and run the script again.

**Script types credentials but login doesn't work**
The CAPTCHA overlay was still on screen when the 15 seconds ran out and the button was clicked. Increase `time.sleep(15)` to `time.sleep(25)` near the CAPTCHA section to give yourself more time.

**Height and weight always show values for class 5**
The class label the portal showed didn't match anything in `CLASS_NAME_MAP`. Open the JSON log and find the `"class"` value for that student. Then open the script, find `CLASS_NAME_MAP`, and add that exact string as a new entry pointing to the correct class number.

**The script clicks but nothing happens on an Angular dropdown**
This portal uses Angular which intercepts normal Selenium clicks. All critical clicks in these scripts already use JavaScript execution (`driver.execute_script`) to get around this. If you add new steps, always use `js_click()` instead of `.click()`.

---

# Disclaimer

These scripts were built for administrative efficiency at a specific school. The randomized values for marks, attendance, phone numbers, admission numbers, height, and weight are approximations. Before using for official UDISE+ submissions, verify that the generated values are acceptable under your school's actual records, or modify the scripts to pull real data from a local spreadsheet or database.
