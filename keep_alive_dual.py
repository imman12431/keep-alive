#!/usr/bin/env python3
"""
Dual Streamlit App Keep-Alive Script
Interacts with both apps:
1. Tennis Backhand Detector - selects Djokovic video and runs detection
2. Document QA Chatbot - asks the first sample question
"""

import time
import logging
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
TENNIS_APP_URL = "https://finalbhdetector.streamlit.app/"
QA_APP_URL = "https://f2pcfewxwnunfssjudhbqk.streamlit.app/"


def setup_driver():
    """Initialize Chrome WebDriver with headless options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Chrome WebDriver initialized successfully")
        return driver
    except WebDriverException as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        raise


def interact_with_tennis_app(driver):
    """
    Navigate to Tennis app and trigger backhand detection on Djokovic video.
    Returns True if successful, False otherwise.
    """
    try:
        logger.info(f"🎾 Navigating to Tennis Backhand Detector: {TENNIS_APP_URL}")
        driver.get(TENNIS_APP_URL)
        
        wait = WebDriverWait(driver, 45)
        
        logger.info("Waiting for page to load...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        time.sleep(5)
        
        logger.info("Page loaded successfully")
        
        # Select "Use demo video"
        logger.info("Selecting demo video option...")
        try:
            radio_labels = driver.find_elements(By.CSS_SELECTOR, "label")
            for label in radio_labels:
                if "Use demo video" in label.text:
                    radio_input = label.find_element(By.CSS_SELECTOR, "input[type='radio']")
                    if not radio_input.is_selected():
                        driver.execute_script("arguments[0].click();", radio_input)
                        time.sleep(2)
                    break
        except Exception as e:
            logger.warning(f"Could not select demo video option: {e}")
        
        # Select "Novak Djokovic"
        logger.info("Selecting Novak Djokovic demo...")
        djokovic_found = False
        
        try:
            radio_labels = driver.find_elements(By.CSS_SELECTOR, "label")
            for label in radio_labels:
                if "Novak Djokovic" in label.text or "Djokovic" in label.text:
                    radio_input = label.find_element(By.CSS_SELECTOR, "input[type='radio']")
                    driver.execute_script("arguments[0].click();", radio_input)
                    time.sleep(3)
                    djokovic_found = True
                    logger.info("✅ Djokovic video selected")
                    break
        except Exception as e:
            logger.warning(f"Error selecting Djokovic: {e}")
        
        if not djokovic_found:
            logger.warning("Could not find Djokovic option")
        
        time.sleep(2)
        
        # Click "Run Backhand Detection"
        logger.info("Looking for Run Backhand Detection button...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        
        detection_started = False
        for button in buttons:
            try:
                if "Run Backhand Detection" in button.text or "▶️" in button.text:
                    logger.info("Clicking Run Backhand Detection button...")
                    driver.execute_script("arguments[0].click();", button)
                    detection_started = True
                    time.sleep(3)
                    logger.info("✅ Button clicked successfully")
                    break
            except Exception as e:
                continue
        
        if not detection_started:
            logger.error("⚠️  Could not find or click Run Backhand Detection button")
            return False
        
        logger.info("Waiting for processing to start...")
        time.sleep(5)
        
        page_source = driver.page_source.lower()
        if "processing" in page_source or "please wait" in page_source:
            logger.info("✅✅ Tennis app: Processing confirmed - app is actively running!")
        else:
            logger.info("✅ Tennis app: Detection triggered successfully!")
        
        return True
        
    except TimeoutException as e:
        logger.error(f"❌ Tennis app: Timeout waiting for page elements: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Tennis app: Error interacting with app: {e}")
        return False


def interact_with_qa_app(driver):
    """
    Navigate to Document QA app and ask the first sample question.
    Returns True if successful, False otherwise.
    """
    try:
        logger.info(f"📄 Navigating to Document QA Chatbot: {QA_APP_URL}")
        driver.get(QA_APP_URL)
        
        wait = WebDriverWait(driver, 45)
        
        logger.info("Waiting for page to load...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        time.sleep(5)
        
        logger.info("Page loaded successfully")
        
        # Look for the first sample question button
        # The first question is: "What was Qatar's nominal GDP in 2020 in billions of Qatari Riyals"
        logger.info("Looking for sample question buttons...")
        
        buttons = driver.find_elements(By.TAG_NAME, "button")
        question_clicked = False
        
        for button in buttons:
            try:
                button_text = button.text
                # Look for the first sample question
                if "Qatar" in button_text and "GDP" in button_text and "2020" in button_text:
                    logger.info(f"Found sample question: {button_text}")
                    logger.info("Clicking sample question button...")
                    driver.execute_script("arguments[0].click();", button)
                    question_clicked = True
                    time.sleep(3)
                    logger.info("✅ Sample question clicked successfully")
                    break
            except Exception as e:
                continue
        
        if not question_clicked:
            logger.warning("⚠️  Could not find sample question button, trying chat input...")
            
            # Try to find chat input and type the question
            try:
                chat_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
                for chat_input in chat_inputs:
                    if chat_input.is_displayed():
                        question = "What was Qatar's nominal GDP in 2020 in billions of Qatari Riyals"
                        chat_input.send_keys(question)
                        time.sleep(1)
                        
                        # Try to submit (look for send button or press Enter)
                        from selenium.webdriver.common.keys import Keys
                        chat_input.send_keys(Keys.RETURN)
                        time.sleep(2)
                        logger.info("✅ Question submitted via chat input")
                        question_clicked = True
                        break
            except Exception as e:
                logger.warning(f"Could not submit via chat input: {e}")
        
        if not question_clicked:
            logger.error("⚠️  Could not ask question")
            return False
        
        # Wait for response
        logger.info("Waiting for response...")
        time.sleep(5)
        
        page_source = driver.page_source.lower()
        if "searching" in page_source or "generating" in page_source:
            logger.info("✅✅ QA app: Processing confirmed - app is actively running!")
        elif "qatar" in page_source or "gdp" in page_source:
            logger.info("✅ QA app: Question processed successfully!")
        else:
            logger.info("✅ QA app: Interaction completed!")
        
        return True
        
    except TimeoutException as e:
        logger.error(f"❌ QA app: Timeout waiting for page elements: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ QA app: Error interacting with app: {e}")
        return False


def main():
    """Execute interactions with both apps."""
    logger.info("=" * 70)
    logger.info("🚀 DUAL STREAMLIT KEEP-ALIVE - ONE-TIME EXECUTION")
    logger.info("=" * 70)
    logger.info(f"Tennis App: {TENNIS_APP_URL}")
    logger.info(f"QA App: {QA_APP_URL}")
    logger.info(f"Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    driver = None
    tennis_success = False
    qa_success = False
    
    try:
        driver = setup_driver()
        
        # Interact with Tennis app
        logger.info("\n" + "=" * 70)
        logger.info("STEP 1: Tennis Backhand Detector")
        logger.info("=" * 70)
        tennis_success = interact_with_tennis_app(driver)
        
        # Wait between apps
        time.sleep(3)
        
        # Interact with QA app
        logger.info("\n" + "=" * 70)
        logger.info("STEP 2: Document QA Chatbot")
        logger.info("=" * 70)
        qa_success = interact_with_qa_app(driver)
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("EXECUTION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Tennis App: {'✅ Success' if tennis_success else '❌ Failed'}")
        logger.info(f"QA App: {'✅ Success' if qa_success else '❌ Failed'}")
        
        if tennis_success and qa_success:
            logger.info("✅ Both apps executed successfully!")
            exit_code = 0
        elif tennis_success or qa_success:
            logger.warning("⚠️  Partial success - one app may have failed")
            exit_code = 1
        else:
            logger.error("❌ Both apps failed")
            exit_code = 2
            
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.exception("Full traceback:")
        exit_code = 2
        
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("WebDriver closed")
            except:
                logger.warning("Could not close WebDriver")
    
    logger.info("=" * 70)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
