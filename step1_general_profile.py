import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

class GeneralProfileUpdater:
    def __init__(self, driver, wait, utils):
        self.driver = driver
        self.wait = wait
        self.utils = utils

    def update(self, student_log):
        try:
            phone_input = self.wait.until(EC.presence_of_element_located((By.ID, "phoneNo")))
            current_value = phone_input.get_attribute("value").strip()

            if current_value in ("9999999991", "9999999999") or not current_value:
                phone_input.clear()
                full_number = "97855" + str(random.randint(10000, 99999))
                phone_input.send_keys(full_number)
                student_log["phone"] = full_number
            else:
                student_log["phone"] = current_value
        except Exception as e:
            print(f"  ❌ Phone number error: {e}")

        time.sleep(0.2)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.3)

        try:
            blood_group_select = Select(self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[formcontrolname='bloodGroup']"))
            ))
            if blood_group_select.first_selected_option.get_attribute("value") == "":
                blood_group_select.select_by_value("9")
        except Exception as e:
            print(f"  ❌ Blood group error: {e}")

        self.utils.js_click("//button[normalize-space(span/text())='Save']")
        time.sleep(0.2)
        print("  ✅ General Profile saved")

        self.utils.js_click_css("div.swal2-actions > button.swal2-confirm")
        time.sleep(0.2)

        self.utils.js_click('//button[@type="button" and @matsteppernext]')
        time.sleep(0.2)
        print("  ✅ Moved to Enrolment Profile tab")
