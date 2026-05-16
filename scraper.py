from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class StudentInfoScraper:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def scrape(self, student_log):
        try:
            info_card = self.wait.until(EC.presence_of_element_located((
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

            print(f"  📋 {student_log.get('name')} | Class: {student_log.get('class')} | "
                  f"Section: {student_log.get('section')} | PEN: {student_log.get('pen')} | "
                  f"Year: {student_log.get('academic_year')}")

        except Exception as e:
            print(f"  ⚠️ Could not read student info card: {e}")
