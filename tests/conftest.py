from selenium import webdriver

def pytest_setup_options():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    # Convert ChromeOptions to dictionary
    return vars(chrome_options)
