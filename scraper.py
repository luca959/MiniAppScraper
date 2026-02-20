from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

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

try:
    driver.get("https://tapps.center/")
    wait = WebDriverWait(driver, 20)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".styles_scrollContainer__ICkJv a[href]")
        )
    )
    print("✅ Iniziato!")

    # 🚀 ABILITA NEW TAB HANDLING
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
            time.sleep(1)
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
                time.sleep(3)

                # 🎯 OPEN BUTTON
                open_xpath = (
                    "/html/body/main/div[1]/div[2]/div[1]/div[2]/div[2]/button[1]/span"
                )
                new_tab_url = ""

                try:
                    open_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, open_xpath))
                    )

                    # 📝 SALVA URL ATTUALE PRIMA
                    before_open_url = driver.current_url

                    # CLICK OPEN
                    driver.execute_script("arguments[0].click();", open_btn)
                    print("       ✅ OPEN cliccato!")
                    time.sleep(3)

                    # 🔑 CATTURA NUOVA TAB
                    all_windows_after = driver.window_handles

                    # Se si apre nuova tab
                    if len(all_windows_after) > len(all_windows):
                        # Switch alla nuova tab
                        new_window = [
                            w for w in all_windows_after if w != original_window
                        ][0]
                        driver.switch_to.window(new_window)

                        # SALVA URL NUOVA PAGINA 🎉
                        new_tab_url = driver.current_url
                        print(f"       🌐 NUOVA TAB URL: {new_tab_url}")

                        # Chiudi nuova tab e torna originale
                        driver.close()
                        driver.switch_to.window(original_window)

                    else:
                        # Se resta stessa tab
                        new_tab_url = driver.current_url
                        print(f"       📄 STESSA TAB URL: {new_tab_url}")

                except Exception as open_e:
                    print(f"       ⚠️ OPEN error: {str(open_e)[:50]}")
                    new_tab_url = driver.current_url

                # Popup handling (stessa tab)
                popup_closed = False
                popup_selectors = [
                    "//button[@aria-label='Close'] | //button[contains(@class,'close')]",
                    ".modal-close",
                    "//svg[@aria-label='close']",
                    "//button[.//span[text()='✕' or text()='X']]",
                ]

                for xpath_sel in popup_selectors:
                    try:
                        close_btn = WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, xpath_sel))
                        )
                        driver.execute_script("arguments[0].click();", close_btn)
                        print("       ✅ Popup chiuso!")
                        popup_closed = True
                        time.sleep(1)
                        break
                    except:
                        continue

                # BACK
                driver.back()
                time.sleep(2)
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".styles_applicationCardLink__uYHrK")
                    )
                )

                # 💾 SALVA TUTTI URL
                apps_data.append(
                    {
                        "categoria": cat_name,
                        "cat_url": cat_url,
                        "app_name": app_name,
                        "card_url": card_url,
                        "before_open_url": before_open_url,
                        "new_tab_open_url": new_tab_url,  # 🎉 QUESTO È QUELLO CHE VUOI!
                        "final_url": driver.current_url,
                    }
                )

                app_index += 1

            print(f"   ✅ {app_index} app")
            driver.back()
            time.sleep(2)
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".styles_scrollContainer__ICkJv a[href]")
                )
            )
            categories_visited.append(cat_name)

        except Exception as e:
            print(f"   ❌: {str(e)[:60]}")
            driver.back()
            time.sleep(3)
            continue

    # CSV
    print(f"\n🎉 {len(apps_data)} app salvate!")
    if apps_data:
        with open("tapps_apps_perfect.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "categoria",
                    "cat_url",
                    "app_name",
                    "card_url",
                    "before_open_url",
                    "new_tab_open_url",
                    "final_url",
                ],
            )
            writer.writeheader()
            writer.writerows(apps_data)
        print(
            "✅ 'tapps_apps_perfect.csv' - new_tab_open_url è quello della nuova pagina!"
        )

    input("\nEnter...")

finally:
    driver.quit()
