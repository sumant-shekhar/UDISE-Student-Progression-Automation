import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class ProfilePreviewComplete:
    def __init__(self, driver, wait, utils):
        self.driver = driver
        self.wait = wait
        self.utils = utils

    def update(self, student_log):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.3)

        self.utils.js_click(
            '/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-edit-student-new-ac/div/div/div/div/div[2]/div/mat-stepper/div/div[2]/div[4]/div/app-preview-new-ac/form/div/div[3]/div[3]/div/button[3]'
        )
        time.sleep(0.2)
        print("  ✅ Complete Data clicked")

        self.utils.js_click('//button[@type="button" and contains(@class, "swal2-cancel")]')
        time.sleep(2)

        try:
            next_btn = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//button[@type="button" and contains(text(), "Next Student")]'
                ))
            )
            self.driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(2)
            print(f"  ✅ Moved to next student")
            student_log["is_last_student"] = False
            return False

        except Exception:
            print(f"  🏁 Last student reached — clicking Back To School Dashboard...")
            try:
                back_btn = self.wait.until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        '/html/body/app-root/app-admin-dashboard/div[2]/div[2]/main/div/div/div/app-edit-student-new-ac/div/div/div/div/div[2]/div/mat-stepper/div/div[2]/div[4]/div/app-preview-new-ac/form/div/div[3]/div[3]/div/button[2]'
                    ))
                )
                self.driver.execute_script("arguments[0].click();", back_btn)
                time.sleep(2)
            except Exception as e:
                print(f"  ⚠️ Back To School Dashboard button not found: {e}")

            student_log["is_last_student"] = True
            return True
