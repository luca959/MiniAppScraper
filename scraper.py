from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)

categories_visited = []
apps_data = []
csv_filename = "tapps_apps_live.csv"

# 📝 INIT CSV (append mode)
fieldnames = [
    "categoria",
    "cat_url",
    "app_name",
    "card_url",
    "before_open_url",
    "new_tab_open_url",
    "final_url",
]
file_exists = os.path.isfile(csv_filename)
with open(csv_filename, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()
        print(f"✅ CSV inizializzato: {csv_filename}")

try:
    driver.get("https://tapps.center/")
    wait = WebDriverWait(driver, 20)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".styles_scrollContainer__ICkJv a[href]")
        )
    )
    print("✅ Iniziato!")

    original_window = driver.current_window_handle
    all_windows = driver.window_handles

    category_links = driver.find_elements(
        By.CSS_SELECTOR, ".styles_scrollContainer__ICkJv a[href]"
    )

    for i in range(len(category_links)):
        try:
            category_links = driver.find_elements(
                By.CSS_SELECTOR, ".styles_scrollContainer__ICkJv a[href]"
            )
            if i >= len(category_links):
                break

            cat_link = category_links[i]
            cat_name = cat_link.text.strip() or f"Cat_{i+1}"
            cat_url = cat_link.get_attribute("href") or ""

            print(f"\n🔄 [{i+1}] '{cat_name}'")

            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", cat_link
            )
            time.sleep(0.5)
            cat_link.click()

            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".styles_applicationCardLink__uYHrK")
                )
            )

            # Loop app
            app_index = 0
            while True:
                app_links = driver.find_elements(
                    By.CSS_SELECTOR, ".styles_applicationCardLink__uYHrK"
                )
                if app_index >= len(app_links):
                    break

                app_link = app_links[app_index]
                app_name = (app_link.text.strip() or f"App_{app_index+1}")[:80]
                card_url = app_link.get_attribute("href") or ""

                print(f"     📱 [{app_index+1}] '{app_name}'")

                # Click app card
                driver.execute_script("arguments[0].click();", app_link)
                time.sleep(0.5)

                # OPEN BUTTON
                open_xpath = (
                    "/html/body/main/div[1]/div[2]/div[1]/div[2]/div[2]/button[1]/span"
                )
                new_tab_url = ""
                before_open_url = driver.current_url

                try:
                    open_btn = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, open_xpath))
                    )
                    driver.execute_script("arguments[0].click();", open_btn)
                    print("       ✅ OPEN!")
                    time.sleep(0.5)

                    # CATTURA NUOVA TAB
                    all_windows_after = driver.window_handles
                    if len(all_windows_after) > len(all_windows):
                        new_window = [
                            w for w in all_windows_after if w != original_window
                        ][0]
                        driver.switch_to.window(new_window)
                        new_tab_url = driver.current_url
                        print(f"       🌐 NEW TAB: {new_tab_url}")
                        driver.close()
                        driver.switch_to.window(original_window)
                    else:
                        new_tab_url = driver.current_url

                except Exception as open_e:
                    print(f"       ⚠️ OPEN: {str(open_e)[:40]}")
                    new_tab_url = driver.current_url

                # Popup
                popup_closed = False
                popup_selectors = [
                    "//button[@aria-label='Close'] | //button[contains(@class,'close')]",
                    ".modal-close",
                    "//svg[@aria-label='close']",
                    "//button[.//span[text()='✕' or text()='X']]",
                ]

                for xpath_sel in popup_selectors:
                    try:
                        close_btn = WebDriverWait(driver, 0.5).until(
                            EC.element_to_be_clickable((By.XPATH, xpath_sel))
                        )
                        driver.execute_script("arguments[0].click();", close_btn)
                        print("       ✅ Popup chiuso!")
                        popup_closed = True
                        time.sleep(0.5)
                        break
                    except:
                        continue

                # BACK
                driver.back()
                time.sleep(0.5)
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".styles_applicationCardLink__uYHrK")
                    )
                )

                # 🚀 SALVA APP NEL CSV SUBITO!
                app_row = {
                    "categoria": cat_name,
                    "cat_url": cat_url,
                    "app_name": app_name,
                    "card_url": card_url,
                    "before_open_url": before_open_url,
                    "new_tab_open_url": new_tab_url,
                    "final_url": driver.current_url,
                }

                with open(csv_filename, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(app_row)

                apps_data.append(app_row)
                print(f"     ✅ APP SALVATA #{len(apps_data)}: {new_tab_url[:80]}...")

                app_index += 1

            print(f"   ✅ {app_index} app")
            driver.back()
            time.sleep(0.5)
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".styles_scrollContainer__ICkJv a[href]")
                )
            )
            categories_visited.append(cat_name)

        except Exception as e:
            print(f"   ❌: {str(e)[:60]}")
            driver.back()
            time.sleep(0.5)
            continue

    print(f"\n🎉 TOTALE: {len(apps_data)} app salvate live!")
    print(f"📄 File: {csv_filename}")

    input("\nEnter...")

finally:
    driver.quit()
