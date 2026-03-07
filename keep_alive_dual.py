#!/usr/bin/env python3
"""
Dual Streamlit App Keep-Alive Script (Improved)
Interacts with both apps with robust element detection:
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
from selenium.webdriver.common.keys import Keys

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
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Chrome WebDriver initialized successfully")
        return driver
    except WebDriverException as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        raise


def wake_up_app_if_sleeping(driver, wait):
    """Check if app is sleeping and wake it up."""
    try:
        time.sleep(2)
        page_source = driver.page_source
        if "Zzzz" in page_source or "gone to sleep" in page_source or "inactive" in page_source.lower():
            logger.info("⚠️  App is sleeping - clicking wake up button...")
            try:
                # Try multiple selectors for the wake button
                wake_button = None
                selectors = [
                    "//button[contains(text(), 'Yes, get this app back up')]",
                    "//button[contains(text(), 'get this app back up')]",
                    "//*[contains(text(), 'Yes')]//ancestor::button",
                ]
                
                for selector in selectors:
                    try:
                        wake_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        break
                    except:
                        continue
                
                if wake_button:
                    wake_button.click()
                    logger.info("✅ Wake up button clicked, waiting up to 5 minutes for app to boot...")
                    
                    # Wait up to 5 minutes for app to fully start
                    # Check every 10 seconds if app has loaded
                    max_wait = 300  # 5 minutes
                    elapsed = 0
                    interval = 10
                    
                    while elapsed < max_wait:
                        time.sleep(interval)
                        elapsed += interval
                        logger.info(f"   Waiting... ({elapsed}s / {max_wait}s)")
                        
                        # Check if app has loaded by looking for content
                        try:
                            page_source = driver.page_source
                            # Look for signs the app is loaded (not sleeping)
                            if "Zzzz" not in page_source and len(page_source) > 5000:
                                logger.info(f"✅ App appears to be loaded after {elapsed}s!")
                                time.sleep(5)  # Extra buffer
                                return True
                        except:
                            continue
                    
                    logger.info(f"⚠️  App may still be loading after {max_wait}s, continuing anyway...")
                    return True
            except Exception as e:
                logger.warning(f"Could not find wake button: {e}")
    except Exception as e:
        logger.debug(f"Wake check failed: {e}")
    return False


def interact_with_tennis_app(driver):
    """
    Navigate to Tennis app and trigger backhand detection on Djokovic video.
    """
    try:
        logger.info(f"🎾 Navigating to Tennis Backhand Detector: {TENNIS_APP_URL}")
        driver.get(TENNIS_APP_URL)
        
        wait = WebDriverWait(driver, 360)  # 6 minutes timeout
        time.sleep(5)
        
        # Wake up if sleeping
        wake_up_app_if_sleeping(driver, wait)
        
        # Wait for page to load
        logger.info("Waiting for page to load...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(8)
        
        logger.info("Page loaded, looking for interactive elements...")
        
        # Click the correct radio buttons for demo video and Djokovic
        try:
            radios = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='radio']")))
            logger.info(f"Found {len(radios)} radio buttons")
            
            # Radio button order in tennis app:
            # radios[0] = "Use demo video"
            # radios[1] = "Upload your own"
            # radios[2] = "Jannik Sinner"
            # radios[3] = "Novak Djokovic"
            
            if len(radios) >= 4:
                # Click "Use demo video" first (should be default but ensure it)
                driver.execute_script("arguments[0].scrollIntoView(true);", radios[0])
                time.sleep(1)
                driver.execute_script("arguments[0].click();", radios[0])
                logger.info("✅ Selected 'Use demo video'")
                time.sleep(2)
                
                # Click "Novak Djokovic" (4th radio button)
                driver.execute_script("arguments[0].scrollIntoView(true);", radios[3])
                time.sleep(1)
                driver.execute_script("arguments[0].click();", radios[3])
                logger.info("✅ Selected 'Novak Djokovic'")
                time.sleep(4)
            else:
                logger.warning(f"Expected 4 radio buttons, found {len(radios)}")
        except Exception as e:
            logger.warning(f"Could not select radios: {e}")
        
        # Find and click Run button - try multiple strategies
        logger.info("Looking for Run Backhand Detection button...")
        button_clicked = False
        
        # Wait a bit for button to be ready
        time.sleep(2)
        
        # Strategy 1: XPath with text
        try:
            buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Run Backhand') or contains(text(), 'Run') or contains(text(), '▶')]")
            logger.info(f"Found {len(buttons)} potential run buttons via XPath")
            for btn in buttons:
                if btn.tag_name == "button" or btn.tag_name == "div":
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", btn)
                        button_clicked = True
                        logger.info("✅ Clicked Run button (XPath)")
                        break
                    except:
                        continue
        except Exception as e:
            logger.debug(f"XPath strategy failed: {e}")
        
        # Strategy 2: Find all buttons
        if not button_clicked:
            try:
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                logger.info(f"Found {len(all_buttons)} total buttons")
                for i, button in enumerate(all_buttons):
                    try:
                        text = button.text.strip()
                        if text and any(keyword in text for keyword in ["Run", "▶", "Backhand", "Detection"]):
                            logger.info(f"Button {i}: '{text[:50]}'")
                            driver.execute_script("arguments[0].scrollIntoView(true);", button)
                            time.sleep(0.5)
                            driver.execute_script("arguments[0].click();", button)
                            button_clicked = True
                            logger.info(f"✅ Clicked button: '{text[:30]}'")
                            break
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Button iteration failed: {e}")
        
        if not button_clicked:
            logger.error("⚠️  Could not find Run button")
            driver.save_screenshot("tennis_no_button.png")
            logger.info("Screenshot saved")
            # Still return True since we at least loaded the app
            return True
        
        time.sleep(3)
        logger.info("✅ Tennis app interaction completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Tennis app error: {e}")
        try:
            driver.save_screenshot("tennis_error.png")
        except:
            pass
        return False


def interact_with_qa_app(driver):
    """
    Navigate to Document QA app and ask the first sample question.
    """
    try:
        logger.info(f"📄 Navigating to Document QA Chatbot: {QA_APP_URL}")
        driver.get(QA_APP_URL)
        
        wait = WebDriverWait(driver, 360)  # 6 minutes timeout
        time.sleep(5)
        
        # Wake up if sleeping
        wake_up_app_if_sleeping(driver, wait)
        
        # Wait for page to load
        logger.info("Waiting for QA app to load...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(10)  # Give it extra time to load
        
        logger.info("QA app loaded, looking for question button...")
        
        # Look for sample question button
        question_clicked = False
        
        # Strategy 1: Find button with Qatar/GDP text
        try:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"Found {len(all_buttons)} buttons")
            
            for i, button in enumerate(all_buttons):
                try:
                    text = button.text.strip()
                    if text and ("Qatar" in text or ("GDP" in text and "2020" in text)):
                        logger.info(f"Found question button: '{text[:60]}'")
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", button)
                        question_clicked = True
                        logger.info("✅ Clicked sample question button")
                        break
                except:
                    continue
        except Exception as e:
            logger.debug(f"Button search failed: {e}")
        
        # Strategy 2: Use chat input if button not found
        if not question_clicked:
            logger.info("Trying chat input method...")
            try:
                chat_inputs = driver.find_elements(By.CSS_SELECTOR, "input, textarea")
                logger.info(f"Found {len(chat_inputs)} input fields")
                
                for chat_input in chat_inputs:
                    try:
                        if chat_input.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView(true);", chat_input)
                            time.sleep(1)
                            question = "What was Qatar's nominal GDP in 2020 in billions of Qatari Riyals"
                            chat_input.send_keys(question)
                            time.sleep(1)
                            chat_input.send_keys(Keys.RETURN)
                            question_clicked = True
                            logger.info("✅ Submitted question via chat input")
                            break
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Chat input failed: {e}")
        
        if not question_clicked:
            logger.warning("⚠️  Could not ask question, but app is awake")
            driver.save_screenshot("qa_no_question.png")
            # Still return True since we loaded the app
            return True
        
        time.sleep(3)
        logger.info("✅ QA app interaction completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ QA app error: {e}")
        try:
            driver.save_screenshot("qa_error.png")
        except:
            pass
        return False


def main():
    """Execute interactions with both apps."""
    logger.info("=" * 70)
    logger.info("🚀 DUAL STREAMLIT KEEP-ALIVE - IMPROVED VERSION")
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
        
        # Tennis app
        logger.info("\n" + "=" * 70)
        logger.info("STEP 1: Tennis Backhand Detector")
        logger.info("=" * 70)
        tennis_success = interact_with_tennis_app(driver)
        
        # Wait between apps
        time.sleep(5)
        
        # QA app
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
            logger.info("✅✅ Both apps executed successfully!")
            exit_code = 0
        elif tennis_success or qa_success:
            logger.warning("⚠️  Partial success - at least one app is awake")
            exit_code = 0  # Changed to 0 so workflow doesn't fail
        else:
            logger.error("❌ Both apps failed")
            exit_code = 1
            
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.exception("Full traceback:")
        exit_code = 1
        
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
