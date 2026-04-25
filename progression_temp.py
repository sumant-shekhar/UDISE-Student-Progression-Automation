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
from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException

from webdriver_manager.chrome import ChromeDriverManager

# ==================== JSON Logger Setup ====================

# File name: 2026-04-25_14-30-55.json  (date_time format, safe for filenames)
LOG_FILENAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_FILENAME)

log_data = {
    "session": {
        "started_at": datetime.now().isoformat(),
        "log_file": LOG_FILENAME,
        "username": "10140615303"
    },
    "summary": {
        "total_students": 0,
        "successful": 0,
        "failed": 0,
        "finished_at": None
    },
    "rows": []
}

def save_log():
    """Save current log_data to JSON file."""
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=4, ensure_ascii=False)

# Save initial log file immediately
save_log()
print(f"📄 Log file created: {LOG_FILENAME}")


# ==================== Helper Function (Stale-Safe) ====================
def safe_js(driver, wait, xpath, script, retries=3):
    """Re-finds element and executes JS, retries if stale."""
    for attempt in range(retries):
        try:
            el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.execute_script(script, el)
            return el
        except StaleElementReferenceException:
            print(f"  ⚠️ Stale element, retrying ({attempt+1}/{retries})...")
            time.sleep(0.5)
    raise Exception(f"Failed after {retries} retries: {xpath}")

def safe_input(driver, wait, xpath, value, retries=3):
    """Re-finds input and sends keys, retries if stale."""
    for attempt in range(retries):
        try:
            el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            el.clear()
            el.send_keys(value)
            return el
        except StaleElementReferenceException:
            print(f"  ⚠️ Stale element, retrying ({attempt+1}/{retries})...")
            time.sleep(0.5)
    raise Exception(f"Failed after {retries} retries: {xpath}")

# ==================== Setup ====================
options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://sdms.udiseplus.gov.in/p0/v1/login?state-id=110")
driver.maximize_window()

wait = WebDriverWait(driver, 20)

# ==================== Login ====================
username_field = wait.until(EC.visibility_of_element_located((By.ID, "username-field")))
username_field.send_keys("10140803009")

password_field = driver.find_element(By.ID, "password-field")
password_field.send_keys("Atul@1234")

# ==================== CAPTCHA (15 sec) ====================
time.sleep(15)

# ==================== Click Login ====================
login_button = wait.until(EC.element_to_be_clickable((By.ID, "submit-btn")))
login_button.click()
print("Login clicked! Waiting for dashboard...")

# ==================== Open Progression Tab manually ====================
time.sleep(35)

print("\n🚀 Automation loop started. Script will continuously check for students...")

# ==================== INFINITE LOOP ADDED HERE ====================
while True:
    # ── Find Total Rows ──
    rows = driver.find_elements(By.XPATH,
        "/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-promotion/div[3]/div/table/tbody/tr"
    )
    total_students = len(rows)
    
    # If no students are visible yet, wait a bit and check again
    if total_students == 0:
        print("👀 No students found on the page. Waiting 10 seconds for you to load a class...")
        time.sleep(20)
        continue  # Loops back to the start of 'while True'
        
    print(f"\nTotal students found: {total_students}")

    # ── Loop Through Each Row ──
    for i in range(1, total_students + 1):

        row_log = {"row_number": i}

        base     = f"/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-promotion/div[3]/div/table/tbody/tr[{i}]/td[2]/ul"
        base_td3 = f"/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-promotion/div[3]/div/table/tbody/tr[{i}]/td[3]/ul[2]"

        print(f"\n── Row {i} ──")

        # ── Step 1: Promoted(by Examination) ──
        safe_js(driver, wait, f"{base}/li[1]/select", "arguments[0].value='1';")
        time.sleep(0.3)
        safe_js(driver, wait, f"{base}/li[1]/select", "arguments[0].dispatchEvent(new Event('change'))")
        time.sleep(0.5)  # Wait for Angular to re-render
        print(f"  ✅ Promoted(by Examination)")

        # ── Step 2: Marks (60–80%) ──
        random_marks = str(random.randint(60, 80))
        safe_input(driver, wait, f"{base}/li[2]/input", random_marks)
        time.sleep(0.5)
        print(f"  ✅ Marks: {random_marks}%")

        # ── Step 3: Days Attended (200–220) ──
        random_days = str(random.randint(200, 220))
        safe_input(driver, wait, f"{base}/li[3]/input", random_days)
        time.sleep(0.5)
        print(f"  ✅ Days: {random_days}")

        # ── Step 4: Schooling Status ──
        try:
            dropdown_xpath = f"{base}/li[4]/select"
            
            # 1. Grab the dropdown element
            select_el = wait.until(EC.presence_of_element_located((By.XPATH, dropdown_xpath)))
            
            # 2. Read the available options
            select_obj = Select(select_el)
            available_values = [opt.get_attribute("value") for opt in select_obj.options]

            # 3. Choose dynamically based on what exists
            if "1" in available_values:
                # "Studying in Same School" is available
                safe_js(driver, wait, dropdown_xpath, "arguments[0].value='1';")
                time.sleep(0.3)
                safe_js(driver, wait, dropdown_xpath, "arguments[0].dispatchEvent(new Event('change'))")
                time.sleep(0.5)
                row_log["schooling_status"] = "Studying in Same School"
                print(f"  ✅ Schooling Status: Same School")
            else:
                # Fallback: "Left School with TC/without TC"
                safe_js(driver, wait, dropdown_xpath, "arguments[0].value='2';")
                time.sleep(0.3)
                safe_js(driver, wait, dropdown_xpath, "arguments[0].dispatchEvent(new Event('change'))")
                time.sleep(0.5)
                row_log["schooling_status"] = "Left School with TC/without TC"
                print(f"  ✅ Schooling Status: Left School with TC/without TC")

        except Exception as e:
            print(f"  ⚠️ Error setting Schooling Status: {e}")

        # ── Step 5: Section A ──
        try:
            safe_js(driver, wait, f"{base_td3}/li[2]/select", "arguments[0].value='1';")
            time.sleep(0.3)
            safe_js(driver, wait, f"{base_td3}/li[2]/select", "arguments[0].dispatchEvent(new Event('change'))")
            time.sleep(0.5)
            print(f"  ✅ Section: A")
        except Exception as e:
            print(f"  ⚠️ Section A not found, skipping: {e}")

        # ── Step 6: Click Update ──
        update_xpath = f"/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-promotion/div[3]/div/table/tbody/tr[{i}]/td[6]/button[1]"
        for attempt in range(3):
            try:
                update_btn = wait.until(EC.element_to_be_clickable((By.XPATH, update_xpath)))
                update_btn.click()
                break
            except StaleElementReferenceException:
                time.sleep(0.5)
        print(f"  ✅ Update clicked")

        # ── Step 7: Click Okay ──
        time.sleep(1)
        okay_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "swal2-confirm")))
        okay_btn.click()
        print(f"  ✅ Okay clicked")

        time.sleep(1)

        # Save the row data and update the success counter
        log_data["rows"].append(row_log)
        log_data["summary"]["successful"] += 1
        log_data["summary"]["total_students"] += 1

    print("\n🎉 All students in this batch updated successfully!")
    
    # Save the logs for this finished batch
    log_data["summary"]["finished_at"] = datetime.now().isoformat()
    save_log()
    print(f"📄 Log updated: {LOG_PATH}")
    
    # Wait 10 seconds to allow the user to shift classes
    print("\n⏳ Waiting 10 seconds for you to select and load the next class...")
    time.sleep(10)