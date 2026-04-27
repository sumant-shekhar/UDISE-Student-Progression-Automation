# ==================== Importing necessary libraries ====================
import sys
import time
import random
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    ElementNotInteractableException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager

# ==================== Credentials — change these before running ====================
USERNAME = "10140615303"
PASSWORD = "58#wwhLG"

# ==================== JSON Logger Setup ====================
# Creates a log file named by current date & time e.g. 2026-04-25_14-30-55.json
LOG_FILENAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_FILENAME)

log_data = {
    "session": {
        "started_at": datetime.now().isoformat(),
        "log_file": LOG_FILENAME,
        "username": USERNAME
    },
    "summary": {
        "total_students": 0,
        "successful": 0,
        "failed": 0,
        "finished_at": None
    },
    "students": []
}

def save_log():
    """Write current log_data to JSON file — called after every student."""
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=4, ensure_ascii=False)

save_log()
print(f"📄 Log file created: {LOG_FILENAME}")

# ==================== Helper Functions (Stale-Safe) ====================
def js_click(driver, wait, xpath, retries=3):
    """Find element by XPath and click it via JavaScript — avoids overlay interceptions."""
    for attempt in range(retries):
        try:
            el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.execute_script("arguments[0].click();", el)
            return el
        except StaleElementReferenceException:
            print(f"  ⚠️ Stale element on click, retrying ({attempt+1}/{retries})...")
            time.sleep(0.5)
    raise Exception(f"js_click failed after {retries} retries: {xpath}")

def js_click_css(driver, wait, css, retries=3):
    """Same as js_click but uses CSS selector instead of XPath."""
    for attempt in range(retries):
        try:
            el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
            driver.execute_script("arguments[0].click();", el)
            return el
        except StaleElementReferenceException:
            print(f"  ⚠️ Stale element on CSS click, retrying ({attempt+1}/{retries})...")
            time.sleep(0.5)
    raise Exception(f"js_click_css failed after {retries} retries: {css}")

# ==================== Height & Weight table (Class 1–10) ====================
# Realistic average values per class, randomized ±5cm / ±3kg per student
CLASS_DATA = {
    1:  {"height_cm": 115, "weight_kg": 21},
    2:  {"height_cm": 122, "weight_kg": 23},
    3:  {"height_cm": 128, "weight_kg": 26},
    4:  {"height_cm": 133, "weight_kg": 29},
    5:  {"height_cm": 138, "weight_kg": 32},
    6:  {"height_cm": 144, "weight_kg": 36},
    7:  {"height_cm": 149, "weight_kg": 40},
    8:  {"height_cm": 156, "weight_kg": 45},
    9:  {"height_cm": 164, "weight_kg": 51},
    10: {"height_cm": 170, "weight_kg": 56},
}

# ==================== Class Name → Number Mapper ====================
# Converts whatever class string the portal shows into a number for CLASS_DATA lookup
# Handles Roman numerals (I–X), digits (1–10), and pre-primary labels
CLASS_NAME_MAP = {
    # Pre-primary — map to class 1 as closest approximation
    "lkg": 1, "ukg": 1, "kg1": 1, "kg2": 1, "pp1": 1, "pp2": 1,
    "nursery": 1, "pre-primary": 1, "preprimary": 1,
    # Roman numerals
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5,
    "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10,
    # Uppercase Roman numerals
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
    "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
    # Digits as strings
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
}

def get_class_number(class_str):
    """Convert portal class label like 'II', 'UKG/KG2/PP1', '5' to an integer 1–10."""
    if not class_str:
        return 5  # safe fallback mid-range
    # Try each slash-separated token (e.g. "UKG/KG2/PP1")
    for token in class_str.replace("-", "").split("/"):
        key = token.strip().lower()
        if key in CLASS_NAME_MAP:
            return CLASS_NAME_MAP[key]
    return 5  # fallback if nothing matched

# ==================== Setting up the Chrome WebDriver ====================
options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://sdms.udiseplus.gov.in/p0/v1/login?state-id=110")
driver.maximize_window()

wait = WebDriverWait(driver, 20)

# ==================== Login ====================
username_field = wait.until(EC.visibility_of_element_located((By.ID, "username-field")))
username_field.send_keys(USERNAME)

password_field = driver.find_element(By.ID, "password-field")
password_field.send_keys(PASSWORD)

# ==================== CAPTCHA — solve manually in 15 seconds ====================
print("⏳ Waiting 15 seconds — please solve the CAPTCHA in the browser...")
time.sleep(15)

# ==================== Click Login via JS (bypasses any overlay) ====================
login_btn = wait.until(EC.presence_of_element_located((By.ID, "submit-btn")))
driver.execute_script("arguments[0].click();", login_btn)
print("✅ Login clicked! Waiting for dashboard...")

log_data["session"]["login_clicked_at"] = datetime.now().isoformat()
save_log()

# ==================== Wait for the first student to load (navigate manually) ====================
print("⏳ Waiting 25 seconds — please open the student edit page...")
time.sleep(25)

# ==================== Main Loop — processes one student per iteration ====================
student_count = 1

while True:
    print(f"\n{'='*50}")
    print(f"  Processing Student #{student_count}")
    print(f"{'='*50}")

    # Each student gets their own log entry
    student_log = {
        "student_number": student_count,
        "timestamp": datetime.now().isoformat(),
        "status": "started",
        # Student identity — filled by info card scraper below
        "name": None,
        "class": None,
        "section": None,
        "academic_year": None,
        "pen": None,
        # Data fields — filled as each step runs
        "phone": None,
        "admission_no": None,
        "height": None,
        "weight": None,
        "is_last_student": False,
        "error": None
    }

    try:

        # ══════════════════════════════════════════
        # STUDENT INFO — Read identity card at top of page
        # Captures Name, Class, Section, Academic Year, PEN
        # before touching any form fields
        # ══════════════════════════════════════════
        try:
            info_card = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div.card.blue15 ul.SchoolViewShow"
            )))
            items = info_card.find_elements(By.TAG_NAME, "li")

            for item in items:
                text = item.text.strip()
                if "Student Name" in text:
                    student_log["name"] = text.split("-", 1)[-1].strip()
                elif "Class" in text:
                    student_log["class"] = text.split("-", 1)[-1].strip()
                elif "Section" in text:
                    student_log["section"] = text.split("-", 1)[-1].strip()
                elif "Academic Year" in text:
                    student_log["academic_year"] = text.split("-", 1)[-1].strip()
                elif "Permanent Education Number" in text:
                    try:
                        student_log["pen"] = item.find_element(By.CSS_SELECTOR, "span.defined").text.strip()
                    except Exception:
                        student_log["pen"] = text.split("-", 1)[-1].strip()

            print(f"  📋 {student_log['name']} | Class: {student_log['class']} | "
                  f"Section: {student_log['section']} | PEN: {student_log['pen']} | "
                  f"Year: {student_log['academic_year']}")

        except Exception as e:
            print(f"  ⚠️ Could not read student info card: {e}")

        # ══════════════════════════════════════════
        # SECTION 1 — General Profile
        # ══════════════════════════════════════════

        # ── 4.1.10 Mobile Number ──
        # Replace placeholder numbers or fill if empty
        try:
            phone_input = wait.until(EC.presence_of_element_located((By.ID, "phoneNo")))
            current_value = phone_input.get_attribute("value").strip()

            if current_value in ("9999999991", "9999999999") or not current_value:
                phone_input.clear()
                full_number = "97855" + str(random.randint(10000, 99999))
                phone_input.send_keys(full_number)
                student_log["phone"] = full_number
                print(f"  ✅ Phone number set: {full_number}")
            else:
                student_log["phone"] = current_value
                print(f"  ℹ️ Phone already valid: {current_value}, skipping.")
        except Exception as e:
            print(f"  ❌ Phone number error: {e}")

        time.sleep(0.5)

        # ── Scroll to bottom so all fields are visible ──
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # ── Blood Group — fill only if empty ──
        try:
            blood_group_select = Select(wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[formcontrolname='bloodGroup']"))
            ))
            if blood_group_select.first_selected_option.get_attribute("value") == "":
                blood_group_select.select_by_value("9")
                print("  ✅ Blood group set to Under Investigation - Result will be updated soon (9)")
            else:
                print("  ℹ️ Blood group already set, skipping.")
        except Exception as e:
            print(f"  ❌ Blood group error: {e}")

        # ── Save General Profile ──
        js_click(driver, wait, "//button[normalize-space(span/text())='Save']")
        time.sleep(0.5)
        print("  ✅ General Profile saved")

        # ── Dismiss the save confirmation popup ──
        js_click_css(driver, wait, "div.swal2-actions > button.swal2-confirm")
        time.sleep(0.5)

        # ── Move to next tab (Enrolment Profile) ──
        js_click(driver, wait, '//button[@type="button" and @matsteppernext]')
        time.sleep(0.5)
        print("  ✅ Moved to Enrolment Profile tab")

        # ══════════════════════════════════════════
        # SECTION 2 — Enrolment Profile
        # ══════════════════════════════════════════

        # ── Scroll down ──
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)

        # ── 4.2.1 Admission Number — fill only if empty ──
        try:
            adm_input = wait.until(EC.presence_of_element_located((By.ID, "admNo")))
            if not adm_input.get_attribute("value").strip():
                adm_no = str(random.randint(10, 99))
                adm_input.send_keys(adm_no)
                student_log["admission_no"] = adm_no
                print(f"  ✅ Admission number filled: {adm_no}")
            else:
                print("  ℹ️ Admission number already set, skipping.")
        except Exception as e:
            print(f"  ❌ Admission number error: {e}")

        time.sleep(0.5)

        # ── 4.2.3(a) Medium of Instruction — set to Hindi if unset ──
        try:
            med_select = Select(wait.until(EC.presence_of_element_located((By.ID, "medium"))))
            if med_select.first_selected_option.text.strip().lower() == "select":
                med_select.select_by_visible_text("4-Hindi")
                print("  ✅ Medium of Instruction set to Hindi")
            else:
                print(f"  ℹ️ Medium already set: {med_select.first_selected_option.text.strip()}, skipping.")
        except Exception as e:
            print(f"  ❌ Medium of Instruction error: {e}")

        # ── 4.2.3(b) Language Group ──
        try:
            lang_select = Select(wait.until(EC.presence_of_element_located((By.ID, "languageGroup"))))
            try:
                lang_select.select_by_visible_text("English_Hindi_Sanskrit")
                print("  ✅ Language group: English_Hindi_Sanskrit")
            except Exception:
                lang_select.select_by_visible_text("Hindi_English_Sanskrit")
                print("  ✅ Language group: Hindi_English_Sanskrit")
        except Exception as e:
            print(f"  ❌ Language group error: {e}")

        time.sleep(0.5)

        # ── 4.2.6(a) Admitted under RTE Section 12C — click NO ──
        try:
            js_click(driver, wait,
                '/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-edit-student-new-ac/div/div/div/div/div[2]/div/mat-stepper/div/div[2]/div[2]/form/div/app-enrolment-edit-new-ac/div/div/div/form/div[1]/div/div/div[10]/div/div[2]/div[2]/input'
            )
            print("  ✅ RTE 12C: NO selected")
        except Exception as e:
            print(f"  ⚠️ RTE 12C not found, skipping: {e}")

        time.sleep(0.5)

        # ── 4.2.4(b) Subjects Group — select based on stream (Arts/Science) ──
        try:
            stream_select_el = wait.until(
                EC.presence_of_element_located((By.XPATH, "//select[@formcontrolname='academicStream']"))
            )
            selected_stream = Select(stream_select_el).first_selected_option.get_attribute("value").strip()
            print(f"  ℹ️ Academic stream value: {selected_stream}")

            subject_options = {
                "1": ["Geography", "History", "Economics"],   # Arts
                "2": ["Physics", "Chemistry", "Mathematics"]  # Science
            }

            if selected_stream in subject_options:
                stream_name = "Arts" if selected_stream == "1" else "Science"
                print(f"  ✅ {stream_name} stream — selecting subjects...")

                # Open the multi-select dropdown
                dropdown_btn = wait.until(EC.element_to_be_clickable((
                    By.XPATH,
                    "//ng-multiselect-dropdown[@formcontrolname='subjectGroup']//span[contains(@class,'dropdown-btn')]"
                )))
                dropdown_btn.click()
                time.sleep(1)

                for subject in subject_options[selected_stream]:
                    try:
                        option = wait.until(EC.element_to_be_clickable((
                            By.XPATH,
                            f"//div[contains(@class,'dropdown-list')]//div[normalize-space(text())='{subject}']"
                        )))
                        try:
                            option.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", option)
                        print(f"    ✅ Subject selected: {subject}")
                        time.sleep(0.5)
                    except Exception:
                        print(f"    ⚠️ Could not select subject: {subject}")
                    time.sleep(1)
            else:
                print("  ℹ️ Stream is not Arts/Science or already set, skipping subjects.")
        except Exception as e:
            print(f"  ⚠️ Academic stream not found, skipping: {e}")

        time.sleep(1)

        # ── Save Enrolment Profile ──
        js_click(driver, wait,
            '/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-edit-student-new-ac/div/div/div/div/div[2]/div/mat-stepper/div/div[2]/div[2]/form/div/app-enrolment-edit-new-ac/div/div/div/form/div[2]/div/button[2]'
        )
        time.sleep(0.5)
        print("  ✅ Enrolment Profile saved")

        # ── Dismiss save popup ──
        js_click_css(driver, wait, ".swal2-cancel")
        time.sleep(0.5)

        # ══════════════════════════════════════════
        # SECTION 3 — Facility / Other Details Profile
        # ══════════════════════════════════════════

        # ── 4.3.1 Facilities provided to student — YES + Free TextBook ──
        try:
            yes_radio = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@type='radio' and @formcontrolname='facProvYN' and @value='1']"
            )))
            driver.execute_script("arguments[0].click();", yes_radio)
            time.sleep(0.5)

            textbook_checkbox = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@type='checkbox' and @id='textbook']"
            )))
            textbook_checkbox.click()
            print("  ✅ Facility: YES + Free TextBook checked")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ❌ Facility YES/TextBook error: {e}")

        # ── 4.3.2 CWSN — value 2 (No) ──
        try:
            js_click_css(driver, wait, "input[formcontrolname='cwsnYN'][value='2']")
            print("  ✅ CWSN: No")
        except Exception as e:
            print(f"  ❌ CWSN error: {e}")

        time.sleep(0.5)

        # ── 4.3.3 Screened for SLD — No ──
        try:
            sld_radio = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@type='radio' and @formcontrolname='screenedForSld' and @value='2']"
            )))
            driver.execute_script("arguments[0].click();", sld_radio)
            print("  ✅ SLD screening: No")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ❌ SLD error: {e}")

        # ── 4.3.4 Screened for ASD — No ──
        try:
            asd_radio = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@type='radio' and @formcontrolname='autismSpectrumDisorder' and @value='2']"
            )))
            driver.execute_script("arguments[0].click();", asd_radio)
            print("  ✅ ASD screening: No")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ❌ ASD error: {e}")

        # ── 4.3.5 Screened for ADHD — No ──
        try:
            adhd_radio = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@type='radio' and @formcontrolname='attentionDeficitHyperactiveDisorder' and @value='2']"
            )))
            driver.execute_script("arguments[0].click();", adhd_radio)
            print("  ✅ ADHD screening: No")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ❌ ADHD error: {e}")

        # ── 4.3.6 Gifted/Talented — No ──
        try:
            gifted_radio = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@type='radio' and @formcontrolname='giftedChildrenYn' and @value='2']"
            )))
            driver.execute_script("arguments[0].click();", gifted_radio)
            print("  ✅ Gifted/Talented: No")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ❌ Gifted/Talented error: {e}")

        # ── 4.3.7 Olympiads/NLC — No ──
        try:
            olympiads_radio = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@type='radio' and @formcontrolname='olympdsNlc' and @value='2']"
            )))
            driver.execute_script("arguments[0].click();", olympiads_radio)
            print("  ✅ Olympiads/NLC: No")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ❌ Olympiads/NLC error: {e}")

        # ── 4.3.8 NCC/NSS — No ──
        try:
            ncc_radio = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@type='radio' and @formcontrolname='nccNssYn' and @value='2']"
            )))
            driver.execute_script("arguments[0].click();", ncc_radio)
            print("  ✅ NCC/NSS: No")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ❌ NCC/NSS error: {e}")

        # ── 4.3.9 Capable of handling digital devices — No ──
        try:
            js_click_css(driver, wait, "input[name='DGC'][value='2']")
            print("  ✅ Digital devices: No")
        except Exception as e:
            print(f"  ❌ Digital devices error: {e}")

        # ── 4.3.10 Height & Weight — auto-detected from student info card ──
        detected_class = get_class_number(student_log.get("class"))
        base_height = CLASS_DATA[detected_class]["height_cm"]
        base_weight = CLASS_DATA[detected_class]["weight_kg"]
        print(f"  ℹ️ Class detected: '{student_log.get('class')}' → mapped to class {detected_class}")
        student_height = str(random.randint(base_height - 5, base_height + 5))
        student_weight = str(random.randint(base_weight - 3, base_weight + 5))

        height_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='height']")))
        height_field.clear()
        height_field.send_keys(student_height)

        weight_field = driver.find_element(By.XPATH, "//input[@id='weight']")
        weight_field.clear()
        weight_field.send_keys(student_weight)

        student_log["height"] = student_height
        student_log["weight"] = student_weight
        print(f"  ✅ Height: {student_height} cm | Weight: {student_weight} kg")

        # ── 4.3.11 Distance from school — value 2 (1–3 km) ──
        distance_dropdown = wait.until(EC.presence_of_element_located((
            By.XPATH, '//select[@formcontrolname="distanceFrmSchool"]'
        )))
        Select(distance_dropdown).select_by_value("2")
        print("  ✅ Distance from school: 1–3 km")
        time.sleep(0.5)

        # ── 4.3.12 Parent education level — value 5 ──
        parent_edu_dropdown = wait.until(EC.presence_of_element_located((
            By.XPATH, '//select[@formcontrolname="parentEducation"]'
        )))
        Select(parent_edu_dropdown).select_by_value("5")
        print("  ✅ Parent education level set")
        time.sleep(0.5)

        # ── Save Other Details / Facility Profile ──
        js_click(driver, wait,
            '/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-edit-student-new-ac/div/div/div/div/div[2]/div/mat-stepper/div/div[2]/div[3]/form/div/app-other-details-edit-new-ac/div/div/div/form/div[2]/div/button[2]'
        )
        time.sleep(0.5)
        print("  ✅ Facility/Other Profile saved")

        # ── Click Next after saving ──
        js_click(driver, wait, "//button[contains(text(),'Next')]")
        time.sleep(0.5)

        # ══════════════════════════════════════════
        # SECTION 4 — Profile Preview & Complete
        # ══════════════════════════════════════════

        # ── Scroll to bottom to see the Complete Data button ──
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # ── Click Complete Data ──
        js_click(driver, wait,
            '/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-edit-student-new-ac/div/div/div/div/div[2]/div/mat-stepper/div/div[2]/div[4]/div/app-preview-new-ac/form/div/div[3]/div[3]/div/button[3]'
        )
        time.sleep(0.5)
        print("  ✅ Complete Data clicked")

        # ── Dismiss the confirmation dialog ──
        js_click(driver, wait, '//button[@type="button" and contains(@class, "swal2-cancel")]')
        time.sleep(2)

        # ── Next Student OR Back to Dashboard (last student detection) ──
        # After the popup, the portal shows either:
        #   "Next Student"       — more students remain, keep going
        #   "Back to Dashboard"  — this was the last student, stop the loop
        try:
            next_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.XPATH, '//button[@type="button" and contains(text(), "Next Student")]'
                ))
            )
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(2)
            print(f"  ✅ Moved to next student")
            student_log["is_last_student"] = False

        except Exception:
            # "Next Student" not found — this is the last student
            # Try clicking "Back to Dashboard" and exit the loop cleanly
            print(f"  🏁 Last student reached — clicking Back To School Dashboard...")
            try:
                back_btn = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        '/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-edit-student-new-ac/div/div/div/div/div[2]/div/mat-stepper/div/div[2]/div[4]/div/app-preview-new-ac/form/div/div[3]/div[3]/div/button[2]'
                    ))
                )
                driver.execute_script("arguments[0].click();", back_btn)
                print(f"  ✅ Back To School Dashboard clicked!")
                time.sleep(2)
            except Exception as e:
                print(f"  ⚠️ Back To School Dashboard button not found: {e}")

            student_log["is_last_student"] = True
            student_log["status"] = "success"
            log_data["summary"]["successful"] += 1
            log_data["summary"]["total_students"] = student_count
            log_data["students"].append(student_log)
            log_data["summary"]["finished_at"] = datetime.now().isoformat()
            save_log()

            print(f"\n🎉 All students processed!")
            print(f"✅ Successful : {log_data['summary']['successful']}")
            print(f"❌ Failed     : {log_data['summary']['failed']}")
            print(f"📄 Log saved  : {LOG_PATH}")
            break  # Exit the while True loop

        # Mark as success in log
        student_log["status"] = "success"
        log_data["summary"]["successful"] += 1

    except Exception as e:
        student_log["status"] = "failed"
        student_log["error"] = str(e)
        log_data["summary"]["failed"] += 1
        print(f"\n  ❌ Student #{student_count} FAILED: {e}")

    finally:
        # Always save log after each student — even if it failed
        log_data["summary"]["total_students"] = student_count
        log_data["students"].append(student_log)
        save_log()

    student_count += 1

# ==================== Finalize Log (runs if loop ever breaks) ====================
log_data["summary"]["finished_at"] = datetime.now().isoformat()
save_log()

print(f"\n🎉 All students processed!")
print(f"✅ Successful : {log_data['summary']['successful']}")
print(f"❌ Failed     : {log_data['summary']['failed']}")
print(f"📄 Log saved  : {LOG_PATH}")
