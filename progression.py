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
    TimeoutException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_utils import WebDriverUtils

# ==================== Credentials — change these before running ====================
USERNAME = "BR71919106"
PASSWORD = "vir81#PE"

class ProgressionUpdater:
    def __init__(self, driver, wait, utils):
        self.driver = driver
        self.wait = wait
        self.utils = utils

    def process_student_row(self, i, failed_rows):
        base = f"/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-promotion/div[3]/div/table/tbody/tr[{i}]/td[2]/ul"
        base_td3 = f"/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-promotion/div[3]/div/table/tbody/tr[{i}]/td[3]/ul[2]"

        print(f"\n── Row {i} ──")

        try:
            self.utils.safe_js(f"{base}/li[1]/select", "arguments[0].value='1';")
            self.utils.dispatch_change(f"{base}/li[1]/select")
            print(f"  ✅ Promoted(by Examination)")
        except Exception as e:
            print(f"  ⚠️ Step 1 (Promotion) failed: {e}")
            raise

        try:
            random_marks = str(random.randint(60, 80))
            self.utils.safe_input(f"{base}/li[2]/input", random_marks)
            time.sleep(0.15)
            print(f"  ✅ Marks: {random_marks}%")
        except Exception as e:
            print(f"  ⚠️ Step 2 (Marks) failed: {e}")
            raise

        try:
            random_days = str(random.randint(200, 220))
            self.utils.safe_input(f"{base}/li[3]/input", random_days)
            time.sleep(0.15)
            print(f"  ✅ Days: {random_days}")
        except Exception as e:
            print(f"  ⚠️ Step 3 (Days) failed: {e}")
            raise

        try:
            dropdown_xpath = f"{base}/li[4]/select"
            select_el = self.wait.until(EC.presence_of_element_located((By.XPATH, dropdown_xpath)))
            select_obj = Select(select_el)
            available_values = [opt.get_attribute("value") for opt in select_obj.options]

            target_value = "1" if "1" in available_values else "2"
            label = "Same School" if target_value == "1" else "Left School with TC/without TC"

            self.utils.safe_js(dropdown_xpath, f"arguments[0].value='{target_value}';")
            self.utils.dispatch_change(dropdown_xpath)
            print(f"  ✅ Schooling Status: {label}")
        except Exception as e:
            print(f"  ⚠️ Step 4 (Schooling Status) failed, skipping: {e}")

        try:
            self.utils.safe_js(f"{base_td3}/li[2]/select", "arguments[0].value='1';")
            self.utils.dispatch_change(f"{base_td3}/li[2]/select")
            print(f"  ✅ Section: A")
        except Exception as e:
            print(f"  ⚠️ Step 5 (Section A) not found, skipping: {e}")

        update_xpath = f"/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-promotion/div[3]/div/table/tbody/tr[{i}]/td[6]/button[1]"
        update_clicked = False
        for attempt in range(3):
            try:
                update_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, update_xpath)))
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
            return

        print(f"  ✅ Update clicked")

        try:
            okay_btn = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "swal2-confirm")))
            okay_btn.click()
            print(f"  ✅ Okay clicked")
        except TimeoutException:
            print(f"  ⚠️ Okay dialog did not appear for row {i} (server may have rejected). Continuing...")
            failed_rows.append(i)
        except Exception as e:
            print(f"  ⚠️ Okay click error for row {i}: {e}")
            failed_rows.append(i)

        time.sleep(0.5)

    def run_loop(self):
        print("\n🚀 Automation loop started. Script will continuously check for students...")
        while True:
            try:
                rows = self.driver.find_elements(By.XPATH,
                    "/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-promotion/div[3]/div/table/tbody/tr"
                )
                total_students = len(rows)

                if total_students == 0:
                    print("👀 No students found. Waiting 10 seconds for you to load a class...")
                    time.sleep(10)
                    continue

                print(f"\nTotal students found: {total_students}")
                failed_rows = []

                for i in range(1, total_students + 1):
                    try:
                        self.process_student_row(i, failed_rows)
                    except Exception as row_err:
                        print(f"  ❌ Row {i} skipped: {row_err}")
                        failed_rows.append(i)
                        time.sleep(0.5)
                        continue

                successful = total_students - len(failed_rows)
                print(f"\n🎉 Batch done — {successful}/{total_students} students updated successfully.")
                if failed_rows:
                    print(f"  ❌ Failed rows (check manually): {failed_rows}")

                print("\n⏳ Waiting 10 seconds for you to select and load the next class...")
                time.sleep(10)

            except WebDriverException as e:
                print(f"\n🔴 Browser error: {e}\n   Retrying in 15 seconds...")
                time.sleep(15)

            except Exception as outer_err:
                print(f"\n🔴 Unexpected error: {outer_err}\n   Retrying in 10 seconds...")
                time.sleep(10)


if __name__ == "__main__":
    options = Options()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://sdms.udiseplus.gov.in/p0/v1/login?state-id=110")
    driver.maximize_window()

    wait = WebDriverWait(driver, 20)
    utils = WebDriverUtils(driver, wait)

    username_field = wait.until(EC.visibility_of_element_located((By.ID, "username-field")))
    username_field.send_keys(USERNAME)

    password_field = wait.until(EC.visibility_of_element_located((By.ID, "password-field")))
    password_field.send_keys(PASSWORD)

    time.sleep(15)

    login_button = wait.until(EC.element_to_be_clickable((By.ID, "submit-btn")))
    login_button.click()
    print("Login clicked! Waiting for dashboard...")

    time.sleep(60)

    time.sleep(35)

    updater = ProgressionUpdater(driver, wait, utils)
    updater.run_loop()
