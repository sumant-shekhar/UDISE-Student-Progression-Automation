import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

class WebDriverUtils:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def safe_js(self, xpath, script, retries=3):
        for attempt in range(retries):
            try:
                el = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                self.driver.execute_script(script, el)
                return el
            except StaleElementReferenceException:
                print(f"  ⚠️ Stale element, retrying ({attempt+1}/{retries})...")
                time.sleep(0.3)
            except TimeoutException:
                raise TimeoutException(f"Element not found within timeout: {xpath}")
        raise Exception(f"safe_js: failed after {retries} retries — {xpath}")

    def safe_input(self, xpath, value, retries=3):
        for attempt in range(retries):
            try:
                el = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                el.clear()
                el.send_keys(value)
                return el
            except StaleElementReferenceException:
                print(f"  ⚠️ Stale element, retrying ({attempt+1}/{retries})...")
                time.sleep(0.3)
            except TimeoutException:
                raise TimeoutException(f"Input not found within timeout: {xpath}")
        raise Exception(f"safe_input: failed after {retries} retries — {xpath}")

    def dispatch_change(self, xpath):
        self.safe_js(xpath, "arguments[0].dispatchEvent(new Event('change'))")
        time.sleep(0.15)

    def js_click(self, xpath, retries=3):
        for attempt in range(retries):
            try:
                el = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].click();", el)
                return el
            except StaleElementReferenceException:
                print(f"  ⚠️ Stale element on click, retrying ({attempt+1}/{retries})...")
                time.sleep(0.2)
        raise Exception(f"js_click failed after {retries} retries: {xpath}")

    def js_click_css(self, css, retries=3):
        for attempt in range(retries):
            try:
                el = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
                self.driver.execute_script("arguments[0].click();", el)
                return el
            except StaleElementReferenceException:
                print(f"  ⚠️ Stale element on CSS click, retrying ({attempt+1}/{retries})...")
                time.sleep(0.2)
        raise Exception(f"js_click_css failed after {retries} retries: {css}")
