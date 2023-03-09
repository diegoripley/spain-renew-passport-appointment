import datetime
import random
import sys
import time
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def send_sms_message():
    """
    Sends SMS message to Diego to check consulate website 
    for an appointment
    """
    import os
    from twilio.rest import Client

    account_sid = ''
    auth_token = ''
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                         body="Check the consulate website.",
                         from_='',
                         to=''
                     )
def check_consulate_appointment():
    """Checks Spain's consulate website for available appointments"""
    url = "https://app.bookitit.com/es/hosteds/widgetdefault/28dbd7e6e06b2996c84fa53fbe52091e7" 
    referer = "https://www.exteriores.gob.es/Consulados/toronto/es/ServiciosConsulares/Paginas/index.aspx?scco=Canad%c3%a1&scd=280&scca=Pasaportes+y+otros+documentos&scs=Pasaportes+-+Requisitos+y+procedimiento+para+obtenerlo" 

    the_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    print(f"Checking consulate website {the_date}")

    try:
        options = webdriver.FirefoxOptions()
        #options.headless = True 

        def interceptor(request):
            request.headers["referer"] = referer

        driver = webdriver.Firefox(options=options)
        driver.request_interceptor = interceptor

        print("Getting URL")
        driver.get(url)

        # Click on 'continuar'
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
        print("Clicking on 'continuar'")
        element.click()

        # Click on 'cita individual'

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

        print("Clicking on 'cita individual'")
        element.click()

        print("Looking for div that contains no hay horas disponibles")
        try:
            element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID,
                                                    "idDivNotAvailableSlotsContainer"))
                )
        except Exception as e:
            print("Did not find hours not available div")
            print("Looking for time slots")
            element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID,
                                                    "idTimeListTable"))
                )
            if element.is_displayed():
                print("There is an available appointment, send SMS")
                driver.get_screenshot_as_file(f"C:\scratch\{the_date}.png")
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
