import time
from datetime import datetime
from database.db import delete_class_entries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

##################################################################################
# close_cookie_popup
#
# Scrapes the Club Pilates website for cookie popup and clicks decline if the
# button can be found.
#
# Inputs:
#   WebDriver: Selenium WebDriver configured to control Chrome navigated
#   to the desired Club Pilates location website.
#
# Outputs:
#   None
#
##################################################################################
def close_cookie_popup(driver):
    try:
        # Find and click the close button for the cookie popup
        cookie_button = driver.find_element(By.ID, "hs-eu-decline-button")
        cookie_button.click()
        time.sleep(2)
    except Exception as e:
        print("No cookie popup found or could not click it", e)

##################################################################################
# check_class_openings
#
# Scrapes the Club Pilates website for available class openings over a two-week 
# period and returns a list of available Flow 1 or 1.5 classes.
#
# Inputs:
#   None
#
# Outputs:
#   list: A list of dictionaries containing details about available classes.
#         Each dictionary includes:
#         - "open_spots": Number of open spots in the class
#         - "level": Class level (Flow 1 or Flow 1.5)
#         - "date": Date of the class
#         - "time": Start time of the class in 24-hour format
#
# Notes:
#   - Uses Selenium to navigate the Club Pilates scheduling page.
#   - Scrapes class details using BeautifulSoup.
#   - Filters out full or waitlisted classes.
#   - Converts class times to 24-hour format for database storage.
#   - Calls delete_class_entries() to remove outdated class records from the database.
#   - Filters out classes that have already started.
##################################################################################
def check_class_openings():
    openings = []

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode

    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://www.clubpilates.com/location/gardencity")

    # Wait for page to load and cookie popup to appear
    time.sleep(3)

    close_cookie_popup(driver)

    # Get 2 weeks' worth of classes
    for week in range(0, 2):  # Looping for 2 weeks

        if week != 0:
            try:
                next_week_button = driver.find_element(By.CLASS_NAME, "location-scheduler__next")
                next_week_button.click()
                time.sleep(2)  # Wait a little for the next week to load
            except NoSuchElementException:
                print("Next week button not found")
            except Exception as e:
                print("Could not click Next Week", e)

        # Wait for the container to be present
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "location-scheduler__days")))

        # Find the total number of buttons before clicking
        total__daily_buttons = len(driver.find_elements(By.CLASS_NAME, "location-scheduler__day"))

        for i in range(total__daily_buttons):
            # Re-fetch buttons list after each click
            buttons = driver.find_elements(By.CLASS_NAME, "location-scheduler__day")

            # Ensure that we don't exceed the available number of buttons
            if i < len(buttons):
                buttons[i].click()

            time.sleep(1)

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # Get class info
            class_type = soup.select("div.location-scheduler__class-title")

            # Class meta data
            row_meta = soup.select("div.location-scheduler__class-start")

            # Class status, we only care if there are open spots
            class_status = soup.select("div.location-scheduler__class-status")

            # Class date taken from the day button
            button_date = soup.select("button.location-scheduler__day ")

            for index in range(len(class_status)):

                # Skip if class is full, on waitlist, or has no text
                if (
                    "Waitlist" in class_status[index].text
                    or not class_status[index].text.strip()
                    or "full" in class_status[index].text
                ):
                    delete_class_entries(button_date[i].get("value"), row_meta[index].text)
                else:
                    start_index = class_type[index].text.find("Flow")
                    substring = class_type[index].text[start_index : start_index + 8]
                    substring = substring.replace("(", "")

                    # We only want Flow 1 or 1.5 openings
                    if "1" in substring:
                        # Convert time to 24hr format to store in db
                        time_str = row_meta[index].text[:7].replace("-", "")
                        converted_time = datetime.strptime(time_str, "%I:%M%p").strftime("%H:%M")

                        # Get current date and time for filtering
                        class_datetime = datetime.strptime(
                            button_date[i].get("value") + " " + converted_time, "%Y-%m-%d %H:%M"
                        )
                        current_datetime = datetime.now()

                        # Only add classes that haven't started yet
                        if class_datetime > current_datetime:
                            openings.append(
                                {
                                    "open_spots": class_status[index].text,
                                    "level": substring,
                                    "date": button_date[i].get("value"),
                                    "time": converted_time,
                                }
                            )

    driver.quit()

    # Print class openings for debugging/logging
    for open_class in openings:
        time_obj = datetime.strptime(open_class["time"], "%H:%M")
        time_12hr = time_obj.strftime("%I:%M %p")
        print(
            "%s | %s | %s | %s"
            % (
                open_class["open_spots"].ljust(12),
                open_class["level"].ljust(8),
                open_class["date"].ljust(10),
                time_12hr.ljust(15),
            )
        )

    return openings
