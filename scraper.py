from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

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

all_apps_data = []

try:
    driver.get("https://tapps.center/")

    wait = WebDriverWait(driver, 20)
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".styles_root__CVyj a[href]"))
    )

    # 1. CICLO CATEGORIE
    category_links = driver.find_elements(By.CSS_SELECTOR, ".styles_root__CVyj a[href]")

    for cat_idx, cat_link in enumerate(category_links):
        try:
            cat_name = (
                cat_link.text.strip() or cat_link.get_attribute("href").split("/")[-1]
            )
            print(
                f"\n📂 [{cat_idx+1}/{len(category_links)}] === {cat_name.upper()} ==="
            )

            # CLICK categoria
            driver.execute_script("arguments[0].scrollIntoView();", cat_link)
            time.sleep(0.5)
            cat_link.click()
            time.sleep(2)

            # Wait pagina categoria
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".styles_root__fllVc"))
            )

            # 2. CICLO APP dentro .styles_root__fllVc
            app_links = driver.find_elements(
                By.CSS_SELECTOR,
                ".styles_root__fllVc a[href], .styles_root__fllVc [data-app-slug]",
            )

            print(f"   📱 Trovate {len(app_links)} app")

            for app_idx, app_link in enumerate(
                app_links[:5]
            ):  # 5 per test, poi toglilo
                try:
                    # Estrai dati APP
                    app_name_elem = app_link.find_element(
                        By.CSS_SELECTOR, "h3, [class*='name'], [class*='title']"
                    )
                    app_name = app_name_elem.text.strip()
                    app_url = app_link.get_attribute("href")

                    print(f"     🔗 [{app_idx+1}] {app_name[:40]}...")

                    # CLICK app
                    driver.execute_script("arguments[0].scrollIntoView();", app_link)
                    time.sleep(0.3)
                    app_link.click()
                    time.sleep(1.5)  # Wait pagina app

                    # Salva dati
                    all_apps_data.append(
                        {"category": cat_name, "app_name": app_name, "app_url": app_url}
                    )

                    # BACK alla lista categoria
                    driver.back()
                    time.sleep(1)
                    wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, ".styles_root__fllVc")
                        )
                    )

                except Exception as e:
                    print(f"     ❌ Errore app {app_idx}: {e}")
                    driver.back()
                    time.sleep(1)
                    continue

            # BACK alla homepage dopo TUTTE le app della categoria
            print(f"   🔙 BACK home da {cat_name}")
            driver.back()
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".styles_root__CVyj a[href]")
                )
            )
            time.sleep(1)

        except Exception as e:
            print(f"❌ Errore categoria {cat_name}: {e}")
            driver.back()
            time.sleep(2)
            continue

    # SALVA DATASET
    with open("complete_telegram_apps.json", "w", encoding="utf-8") as f:
        json.dump(all_apps_data, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 COMPLETATO! {len(all_apps_data)} app estratte e salvate!")

    input("Premi Enter per chiudere...")

finally:
    driver.quit()
