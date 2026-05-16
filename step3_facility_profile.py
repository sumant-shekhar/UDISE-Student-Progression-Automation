import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

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

CLASS_NAME_MAP = {
    "lkg": 1, "ukg": 1, "kg1": 1, "kg2": 1, "pp1": 1, "pp2": 1,
    "nursery": 1, "pre-primary": 1, "preprimary": 1,
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5,
    "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10,
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
    "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
}

def get_class_number(class_str):
    if not class_str:
        return 5
    for token in class_str.replace("-", "").split("/"):
        key = token.strip().lower()
        if key in CLASS_NAME_MAP:
            return CLASS_NAME_MAP[key]
    return 5

class FacilityProfileUpdater:
    def __init__(self, driver, wait, utils):
        self.driver = driver
        self.wait = wait
        self.utils = utils

    def update(self, student_log):
        try:
            yes_radio = self.wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@type='radio' and @formcontrolname='facProvYN' and @value='1']"
            )))
            self.driver.execute_script("arguments[0].click();", yes_radio)
            time.sleep(0.2)

            textbook_checkbox = self.wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@type='checkbox' and @id='textbook']"
            )))
            textbook_checkbox.click()
            time.sleep(0.2)
        except Exception as e:
            print(f"  ❌ Facility YES/TextBook error: {e}")

        try:
            self.utils.js_click_css("input[formcontrolname='cwsnYN'][value='2']")
        except Exception as e:
            print(f"  ❌ CWSN error: {e}")
        time.sleep(0.2)

        for field_name, value in [
            ('screenedForSld', '2'),
            ('autismSpectrumDisorder', '2'),
            ('attentionDeficitHyperactiveDisorder', '2'),
            ('giftedChildrenYn', '2'),
            ('olympdsNlc', '2'),
            ('nccNssYn', '2')
        ]:
            try:
                radio = self.wait.until(EC.presence_of_element_located((
                    By.XPATH, f"//input[@type='radio' and @formcontrolname='{field_name}' and @value='{value}']"
                )))
                self.driver.execute_script("arguments[0].click();", radio)
                time.sleep(0.2)
            except Exception as e:
                print(f"  ❌ {field_name} error: {e}")

        try:
            self.utils.js_click_css("input[name='DGC'][value='2']")
        except Exception as e:
            print(f"  ❌ Digital devices error: {e}")

        detected_class = get_class_number(student_log.get("class"))
        base_height = CLASS_DATA[detected_class]["height_cm"]
        base_weight = CLASS_DATA[detected_class]["weight_kg"]
        student_height = str(random.randint(base_height - 5, base_height + 5))
        student_weight = str(random.randint(base_weight - 3, base_weight + 5))

        height_field = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='height']")))
        height_field.clear()
        height_field.send_keys(student_height)

        weight_field = self.driver.find_element(By.XPATH, "//input[@id='weight']")
        weight_field.clear()
        weight_field.send_keys(student_weight)

        student_log["height"] = student_height
        student_log["weight"] = student_weight

        distance_dropdown = self.wait.until(EC.presence_of_element_located((
            By.XPATH, '//select[@formcontrolname="distanceFrmSchool"]'
        )))
        Select(distance_dropdown).select_by_value("2")
        time.sleep(0.2)

        parent_edu_dropdown = self.wait.until(EC.presence_of_element_located((
            By.XPATH, '//select[@formcontrolname="parentEducation"]'
        )))
        Select(parent_edu_dropdown).select_by_value("5")
        time.sleep(0.2)

        self.utils.js_click(
            '/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-edit-student-new-ac/div/div/div/div/div[2]/div/mat-stepper/div/div[2]/div[3]/form/div/app-other-details-edit-new-ac/div/div/div/form/div[2]/div/button[2]'
        )
        time.sleep(0.2)
        print("  ✅ Facility/Other Profile saved")

        self.utils.js_click("//button[contains(text(),'Next')]")
        time.sleep(0.2)
