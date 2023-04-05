import datetime
import os
import random
import sys
import time
from dotenv import load_dotenv
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twilio.rest import Client

load_dotenv()

def send_sms_message():
    """
    Sends SMS message when there is an available appointment
    """
    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
    from_number = os.getenv('FROM_NUMBER')
    to_number = os.getenv('TO_NUMBER')

    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                         body="Check the consulate website.",
                         from_=from_number,
                         to=to_number
                     )
def check_consulate_appointment():
    """Checks Spain's consulate website for available appointments"""
    url = "https://app.bookitit.com/es/hosteds/widgetdefault/28dbd7e6e06b2996c84fa53fbe52091e7"
    referer = "https://www.exteriores.gob.es/Consulados/toronto/es/ServiciosConsulares/Paginas/index.aspx?scco=Canad%c3%a1&scd=280&scca=Pasaportes+y+otros+documentos&scs=Pasaportes+-+Requisitos+y+procedimiento+para+obtenerlo"

    the_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    print(f"Checking consulate website {the_date}")

    try:
        options = webdriver.FirefoxOptions()
        options.headless = True 

        def interceptor(request):
            request.headers["referer"] = referer

        driver = webdriver.Firefox(options=options)
        driver.request_interceptor = interceptor

        print(f"Starting appointment check at {url}")
        driver.get(url)

        # Click on 'continuar' (continue)
        element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='bktContinue']/div"))
            )

        element_shown = False
        counter = 0
        while element_shown == False:
            if counter == 0:
                print("Continue button not yet shown")
            counter += 1
            element_shown = element.is_displayed()
            time.sleep(1)
        print("Clicking on 'continuar' (continue)")
        element.click()

        # Click on 'cita individual' (individual appointment)
        element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//div[@id='idListServices']/a/div/div"))
            )

        element_shown = False
        counter = 0
        while element_shown == False:
            if counter == 0:
                print("Cita individual [A] not yet shown")
            counter += 1
            element_shown = element.is_displayed()
            time.sleep(1)

        print("Clicking on 'cita individual' (individual appointment)")
        element.click()

        # Look for div that says there are no available appointments
        print("Looking for div that contains 'no hay horas disponibles' (no available appointments)")
        try:
            element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID,
                                                    "idDivNotAvailableSlotsContainer"))
                )
        except Exception as e:
            print("Did not find no available appointments div")
            print("Looking for time slots")
            element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID,
                                                    "idTimeListTable"))
                )
            if element.is_displayed():
                print("There is an available appointment, send SMS")
                send_sms_message()
                sys.exit()
    except Exception as e:
        print("Failed at something")
        print(e)
    finally:
        driver.close()

    while True:
        check_consulate_appointment()
        time.sleep(random.randrange(30, 60))
