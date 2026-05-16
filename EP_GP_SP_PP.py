# ==================== Importing necessary libraries ====================
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from logger_utils import JSONLogger
from webdriver_utils import WebDriverUtils
from scraper import StudentInfoScraper
from step1_general_profile import GeneralProfileUpdater
from step2_enrolment_profile import EnrolmentProfileUpdater
from step3_facility_profile import FacilityProfileUpdater
from step4_profile_preview import ProfilePreviewComplete

# ==================== Credentials — change these before running ====================
USERNAME = "10140615303"
PASSWORD = "58#wwhLG"

# ==================== Setting up the Chrome WebDriver ====================
if __name__ == "__main__":
    options = Options()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://sdms.udiseplus.gov.in/p0/v1/login?state-id=110")
    driver.maximize_window()

    wait = WebDriverWait(driver, 20)
    utils = WebDriverUtils(driver, wait)
    logger = JSONLogger(USERNAME)
    scraper = StudentInfoScraper(driver, wait)
    gp_updater = GeneralProfileUpdater(driver, wait, utils)
    ep_updater = EnrolmentProfileUpdater(driver, wait, utils)
    sp_updater = FacilityProfileUpdater(driver, wait, utils)
    pp_updater = ProfilePreviewComplete(driver, wait, utils)

    # ==================== Login ====================
    username_field = wait.until(EC.visibility_of_element_located((By.ID, "username-field")))
    username_field.send_keys(USERNAME)

    password_field = driver.find_element(By.ID, "password-field")
    password_field.send_keys(PASSWORD)

    # ==================== CAPTCHA — solve manually in 15 seconds ====================
    print("⏳ Waiting 15 seconds — please solve the CAPTCHA in the browser...")
    time.sleep(15)

    # ==================== Click Login via JS ====================
    login_btn = wait.until(EC.presence_of_element_located((By.ID, "submit-btn")))
    driver.execute_script("arguments[0].click();", login_btn)
    print("✅ Login clicked! Waiting for dashboard...")

    logger.mark_login_clicked()

    # ==================== Wait for the first student to load ====================
    print("⏳ Waiting 25 seconds — please open the student edit page...")
    time.sleep(25)

    # ==================== Main Loop ====================
    student_count = 1

    while True:
        print(f"\n{'='*50}")
        print(f"  Processing Student #{student_count}")
        print(f"{'='*50}")

        student_log = {
            "student_number": student_count,
            "timestamp": datetime.now().isoformat(),
            "status": "started",
            "name": None, "class": None, "section": None, "academic_year": None, "pen": None,
            "phone": None, "admission_no": None, "height": None, "weight": None,
            "is_last_student": False, "error": None
        }

        try:
            scraper.scrape(student_log)
            gp_updater.update(student_log)
            ep_updater.update(student_log)
            sp_updater.update(student_log)
            is_last = pp_updater.update(student_log)

            student_log["status"] = "success"
            logger.update_summary(student_count, logger.log_data["summary"]["successful"] + 1, logger.log_data["summary"]["failed"])
            logger.add_student_log(student_log)

            if is_last:
                print(f"\n🎉 All students processed!")
                print(f"❌ Failed     : {logger.log_data['summary']['failed']}")
                print(f"📄 Log saved  : {logger.log_path}")
                break

        except Exception as e:
            student_log["status"] = "failed"
            student_log["error"] = str(e)
            logger.update_summary(student_count, logger.log_data["summary"]["successful"], logger.log_data["summary"]["failed"] + 1)
            logger.add_student_log(student_log)
            
            print(f"\n  ❌ Student #{student_count} FAILED: {e}")
            print("  🛑 Fatal error encountered. Stopping to prevent infinite error loops.")
            print("  👉 Please fix the page manually, navigate to the next student, and restart the script.")
            break

        student_count += 1

    logger.update_summary(student_count, logger.log_data["summary"]["successful"], logger.log_data["summary"]["failed"], finished=True)
    print(f"\n🎉 All students processed!")
    print(f"❌ Failed     : {logger.log_data['summary']['failed']}")
    print(f"📄 Log saved  : {logger.log_path}")
