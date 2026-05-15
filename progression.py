
# ==================== Importing necessary libraries ====================
import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,           # was missing — any timeout silently crashed the script
    NoSuchElementException,
    ElementNotInteractableException,
    WebDriverException,
)

from webdriver_manager.chrome import ChromeDriverManager

# ==================== Credentials — change these before running ====================
USERNAME = "BR71919106"
PASSWORD = "vir81#PE"

# ==================== Helper Functions (Stale-Safe) ====================
def safe_js(driver, wait, xpath, script, retries=3):
    """
    Re-finds element and executes JS.
    Retries on StaleElementReferenceException.
    Raises cleanly after all retries — caller must handle.
    """
    for attempt in range(retries):
        try:
            el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.execute_script(script, el)
            return el
        except StaleElementReferenceException:
            print(f"  ⚠️ Stale element, retrying ({attempt+1}/{retries})...")
            time.sleep(0.3)
        except TimeoutException:
            raise TimeoutException(f"Element not found within timeout: {xpath}")
    raise Exception(f"safe_js: failed after {retries} retries — {xpath}")


def safe_input(driver, wait, xpath, value, retries=3):
    """
    Re-finds input and sends keys.
    Retries on StaleElementReferenceException.
    """
    for attempt in range(retries):
        try:
            el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            el.clear()
            el.send_keys(value)
            return el
        except StaleElementReferenceException:
            print(f"  ⚠️ Stale element, retrying ({attempt+1}/{retries})...")
            time.sleep(0.3)
        except TimeoutException:
            raise TimeoutException(f"Input not found within timeout: {xpath}")
    raise Exception(f"safe_input: failed after {retries} retries — {xpath}")


def dispatch_change(driver, wait, xpath):
    """Fires Angular change event. Minimal render wait after."""
    safe_js(driver, wait, xpath, "arguments[0].dispatchEvent(new Event('change'))")
    time.sleep(0.15)


# ==================== Setup ====================
options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://sdms.udiseplus.gov.in/p0/v1/login?state-id=110")
driver.maximize_window()

wait = WebDriverWait(driver, 20)

# ==================== Login ====================
username_field = wait.until(EC.visibility_of_element_located((By.ID, "username-field")))
username_field.send_keys(USERNAME)

# FIX: was driver.find_element (no wait) — crashes immediately if DOM is slow
password_field = wait.until(EC.visibility_of_element_located((By.ID, "password-field")))
password_field.send_keys(PASSWORD)

# ==================== CAPTCHA (15 sec) ====================
time.sleep(15)

# ==================== Click Login ====================
login_button = wait.until(EC.element_to_be_clickable((By.ID, "submit-btn")))
login_button.click()
print("Login clicked! Waiting for dashboard...")

# Waiting for block Login OTP
time.sleep(60)

# ==================== Open Progression Tab manually ====================
time.sleep(35)

print("\n🚀 Automation loop started. Script will continuously check for students...")

# ==================== MAIN LOOP ====================
while True:
    # FIX: outer try/except was completely absent — any crash killed ALL remaining classes permanently
    try:
        # ── Find Total Rows ──
        rows = driver.find_elements(By.XPATH,
            "/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-promotion/div[3]/div/table/tbody/tr"
        )
        total_students = len(rows)

        if total_students == 0:
            print("👀 No students found. Waiting 10 seconds for you to load a class...")
            time.sleep(10)
            continue

        print(f"\nTotal students found: {total_students}")
        failed_rows = []

        # ── Loop Through Each Row ──
        for i in range(1, total_students + 1):

            # FIX: per-student try/except — one bad row skips that student only, not the whole class
            try:
                base     = f"/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-promotion/div[3]/div/table/tbody/tr[{i}]/td[2]/ul"
                base_td3 = f"/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-promotion/div[3]/div/table/tbody/tr[{i}]/td[3]/ul[2]"

                print(f"\n── Row {i} ──")

                # ── Step 1: Promoted(by Examination) ──
                # FIX: was unprotected — failure here crashed the entire script
                try:
                    safe_js(driver, wait, f"{base}/li[1]/select", "arguments[0].value='1';")
                    dispatch_change(driver, wait, f"{base}/li[1]/select")
                    print(f"  ✅ Promoted(by Examination)")
                except Exception as e:
                    print(f"  ⚠️ Step 1 (Promotion) failed: {e}")
                    raise  # escalate — skip student cleanly

                # ── Step 2: Marks (60–80%) ──
                # FIX: was unprotected
                try:
                    random_marks = str(random.randint(60, 80))
                    safe_input(driver, wait, f"{base}/li[2]/input", random_marks)
                    time.sleep(0.15)
                    print(f"  ✅ Marks: {random_marks}%")
                except Exception as e:
                    print(f"  ⚠️ Step 2 (Marks) failed: {e}")
                    raise

                # ── Step 3: Days Attended (200–220) ──
                # FIX: was unprotected
                try:
                    random_days = str(random.randint(200, 220))
                    safe_input(driver, wait, f"{base}/li[3]/input", random_days)
                    time.sleep(0.15)
                    print(f"  ✅ Days: {random_days}")
                except Exception as e:
                    print(f"  ⚠️ Step 3 (Days) failed: {e}")
                    raise

                # ── Step 4: Schooling Status ──
                try:
                    dropdown_xpath = f"{base}/li[4]/select"
                    select_el = wait.until(EC.presence_of_element_located((By.XPATH, dropdown_xpath)))
                    select_obj = Select(select_el)
                    available_values = [opt.get_attribute("value") for opt in select_obj.options]

                    target_value = "1" if "1" in available_values else "2"
                    label = "Same School" if target_value == "1" else "Left School with TC/without TC"

                    safe_js(driver, wait, dropdown_xpath, f"arguments[0].value='{target_value}';")
                    dispatch_change(driver, wait, dropdown_xpath)
                    print(f"  ✅ Schooling Status: {label}")
                except Exception as e:
                    print(f"  ⚠️ Step 4 (Schooling Status) failed, skipping: {e}")

                # ── Step 5: Section A ──
                try:
                    safe_js(driver, wait, f"{base_td3}/li[2]/select", "arguments[0].value='1';")
                    dispatch_change(driver, wait, f"{base_td3}/li[2]/select")
                    print(f"  ✅ Section: A")
                except Exception as e:
                    print(f"  ⚠️ Step 5 (Section A) not found, skipping: {e}")

                # ── Step 6: Click Update ──
                # FIX: added update_clicked flag — previously all 3 retries could fail silently
                # and code would fall through to Step 7 as if the click succeeded
                update_xpath = f"/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-promotion/div[3]/div/table/tbody/tr[{i}]/td[6]/button[1]"
                update_clicked = False
                for attempt in range(3):
                    try:
                        update_btn = wait.until(EC.element_to_be_clickable((By.XPATH, update_xpath)))
                        update_btn.click()
                        update_clicked = True
                        break
                    except StaleElementReferenceException:
                        print(f"  ⚠️ Update button stale, retrying ({attempt+1}/3)...")
                        time.sleep(0.3)
                    except TimeoutException:
                        print(f"  ⚠️ Update button not clickable, retrying ({attempt+1}/3)...")
                        time.sleep(0.5)

                if not update_clicked:
                    print(f"  ❌ Update failed after 3 retries — skipping row {i}")
                    failed_rows.append(i)
                    continue

                print(f"  ✅ Update clicked")

                # ── Step 7: Click Okay ──
                # FIX: was completely unprotected — if swal2 dialog never appeared
                # (server error, slow network, rejected save), TimeoutException crashed the entire loop
                try:
                    okay_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "swal2-confirm")))
                    okay_btn.click()
                    print(f"  ✅ Okay clicked")
                except TimeoutException:
                    print(f"  ⚠️ Okay dialog did not appear for row {i} (server may have rejected). Continuing...")
                    failed_rows.append(i)
                except Exception as e:
                    print(f"  ⚠️ Okay click error for row {i}: {e}")
                    failed_rows.append(i)

                time.sleep(0.5)

            except Exception as row_err:
                # Per-row safety net: one failed student never kills the rest
                print(f"  ❌ Row {i} skipped: {row_err}")
                failed_rows.append(i)
                time.sleep(0.5)
                continue

        # ── Batch Summary ──
        successful = total_students - len(failed_rows)
        print(f"\n🎉 Batch done — {successful}/{total_students} students updated successfully.")
        if failed_rows:
            print(f"  ❌ Failed rows (check manually): {failed_rows}")

        print("\n⏳ Waiting 10 seconds for you to select and load the next class...")
        time.sleep(10)

    except WebDriverException as e:
        # Browser crashed or connection lost — wait and retry instead of dying
        print(f"\n🔴 Browser error: {e}\n   Retrying in 15 seconds...")
        time.sleep(15)

    except Exception as outer_err:
        # Catch-all: any unexpected error recovers and retries the loop
        print(f"\n🔴 Unexpected error: {outer_err}\n   Retrying in 10 seconds...")
        time.sleep(10)
