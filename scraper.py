from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Config Chrome anti-detection
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

try:
    # Vai alla homepage
    driver.get("https://tapps.center/")

    # Wait per caricamento categorie
    wait = WebDriverWait(driver, 20)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".styles_scrollContainer__ICkJv a[href]")
        )
    )

    print("✅ Categorie caricate!")

    # TROVA TUTTE LE CATEGORIE
    category_links = driver.find_elements(
        By.CSS_SELECTOR, ".styles_scrollContainer__ICkJv a[href]"
    )
    print(f"📂 Trovate {len(category_links)} categorie:")

    for i, cat_link in enumerate(category_links):
        try:
            # Estrai nome categoria dal testo o href
            cat_text = cat_link.text.strip()
            cat_href = cat_link.get_attribute("href")
            cat_name = cat_text if cat_text else cat_href.split("/")[-1]

            print(f"\n🔄 [{i+1}/{len(category_links)}] Cliccando: '{cat_name}'")

            # SCROLL per renderla visibile
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", cat_link
            )
            time.sleep(1)

            # CLICK categoria
            cat_link.click()
            print("   ⏳ Caricando pagina categoria...")

            # Wait per caricamento pagina categoria (controlla presenza app o header)
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".styles_applicationCardLink__uYHrK")
                    ),
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".styles_header__XSRw")
                    ),
                )
            )

            print(f"   ✅ '{cat_name}' caricata! (pausa 3s)")
            time.sleep(0.1)  # PAUSA per vedere

            # BACK alla homepage
            driver.back()
            print("   🔙 BACK alla homepage...")

            # Wait per tornare alle categorie
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".styles_scrollContainer__ICkJv a[href]")
                )
            )
            time.sleep(1)

            categories_visited.append(cat_name)

        except Exception as e:
            print(f"   ❌ Errore '{cat_name}': {e}")
            # Se si blocca, BACK forzato
            driver.back()
            time.sleep(2)
            continue

    print(f"\n🎉 Visitato {len(categories_visited)}/{len(category_links)} categorie:")
    for cat in categories_visited:
        print(f"  - {cat}")

    input("\nPremi Enter per chiudere il browser...")

finally:
    driver.quit()
