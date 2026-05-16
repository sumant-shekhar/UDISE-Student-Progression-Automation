import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

class EnrolmentProfileUpdater:
    def __init__(self, driver, wait, utils):
        self.driver = driver
        self.wait = wait
        self.utils = utils

    def update(self, student_log):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.2)

        try:
            adm_input = self.wait.until(EC.presence_of_element_located((By.ID, "admNo")))
            if not adm_input.get_attribute("value").strip():
                adm_no = str(random.randint(10, 99))
                adm_input.send_keys(adm_no)
                student_log["admission_no"] = adm_no
        except Exception as e:
            print(f"  ❌ Admission number error: {e}")

        time.sleep(0.2)

        try:
            med_select = Select(self.wait.until(EC.presence_of_element_located((By.ID, "medium"))))
            if med_select.first_selected_option.text.strip().lower() == "select":
                med_select.select_by_visible_text("4-Hindi")
        except Exception as e:
            print(f"  ❌ Medium of Instruction error: {e}")

        try:
            lang_select = Select(self.wait.until(EC.presence_of_element_located((By.ID, "languageGroup"))))
            try:
                lang_select.select_by_visible_text("English_Hindi_Sanskrit")
            except Exception:
                lang_select.select_by_visible_text("Hindi_English_Sanskrit")
        except Exception as e:
            print(f"  ❌ Language group error: {e}")

        time.sleep(0.2)

        try:
            self.utils.js_click(
                '/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-edit-student-new-ac/div/div/div/div/div[2]/div/mat-stepper/div/div[2]/div[2]/form/div/app-enrolment-edit-new-ac/div/div/div/form/div[1]/div/div/div[10]/div/div[2]/div[2]/input'
            )
        except Exception as e:
            print(f"  ⚠️ RTE 12C not found, skipping: {e}")

        time.sleep(0.2)

        try:
            stream_select_el = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//select[@formcontrolname='academicStream']"))
            )
            selected_stream = Select(stream_select_el).first_selected_option.get_attribute("value").strip()

            subject_options = {
                "1": ["Geography", "History", "Economics"],
                "2": ["Physics", "Chemistry", "Mathematics"]
            }

            if selected_stream in subject_options:
                dropdown_btn = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH,
                    "//ng-multiselect-dropdown[@formcontrolname='subjectGroup']//span[contains(@class,'dropdown-btn')]"
                )))
                dropdown_btn.click()
                time.sleep(0.3)

                for subject in subject_options[selected_stream]:
                    try:
                        option = self.wait.until(EC.element_to_be_clickable((
                            By.XPATH,
                            f"//div[contains(@class,'dropdown-list')]//div[normalize-space(text())='{subject}']"
                        )))
                        try:
                            option.click()
                        except Exception:
                            self.driver.execute_script("arguments[0].click();", option)
                        time.sleep(0.2)
                    except Exception:
                        print(f"    ⚠️ Could not select subject: {subject}")
                    time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️ Academic stream not found, skipping: {e}")

        time.sleep(0.3)

        self.utils.js_click(
            '/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-edit-student-new-ac/div/div/div/div/div[2]/div/mat-stepper/div/div[2]/div[2]/form/div/app-enrolment-edit-new-ac/div/div/div/form/div[2]/div/button[2]'
        )
        time.sleep(0.2)
        print("  ✅ Enrolment Profile saved")

        self.utils.js_click_css(".swal2-cancel")
        time.sleep(0.2)
