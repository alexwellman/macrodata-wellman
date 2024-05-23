from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time

# URL of the page you want to visit
url = 'https://www.frbsf.org/economic-research/indicators-data/total-factor-productivity-tfp/'

# Specify the local path where you want the file to be saved
download_path = '/Users/alexwellman/Documents/SIEPR/GitHub/macrodata-wellman/Econ212/Import'

# Set up the Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless") 
chrome_options.add_experimental_option('prefs', {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# Set up the Chrome driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navigate to the URL
driver.get(url)

# Wait for the page to load completely
time.sleep(10)

try:
    # Find the "Download latest dataset" link and click it
    download_link = driver.find_element(By.LINK_TEXT, 'Download latest dataset')
    download_link.click()

    # Wait for the download to start, you may need to adjust the sleep time based on your internet speed
    time.sleep(15)
finally:
    # Close the browser
    driver.quit()

# Inform the user that download is complete
print(f'Download completed. The dataset should be in the directory: {download_path}')