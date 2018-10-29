import sys
import json
import codecs
import configparser
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException


"""
serializa objecto a json y lo guarda en un archivo
"""
def saveAsJSON(obj, file_name):
    json_output = json.dumps(obj, sort_keys=False, ensure_ascii=False, indent=4, separators=(',', ': '))
    file = codecs.open(file_name, "w", "utf-8")
    file.write(json_output)
    file.close()
    return True


"""
Carga datos de archivo de configuracion
"""
def load_settings(config_file, section_name):
    settings = None
    config_parser = configparser.RawConfigParser()
    config_file_path = config_file
    config_parser.read(config_file_path)
    settings = {
        'driver_path': config_parser.get(section_name, 'DRIVER_PATH'),
        'browser_profile': config_parser.get(section_name, 'BROWSER_PROFILE'),
        'url': config_parser.get(section_name, 'URL')
    }
    return settings


"""
Inicializa selenium con chrome y settings correspondientes
"""
def init_selenium(settings,args=None):
    browser = None
    chrome_options = webdriver.ChromeOptions()
    
    if settings['browser_profile']:
        chrome_options.add_argument("user-data-dir=" + settings['browser_profile'])
    
    if args and len(args)>0:
        for arg in args:
            chrome_options.add_argument(arg)
    
    browser = webdriver.Chrome(executable_path=settings['driver_path'], chrome_options=chrome_options)
    return browser


"""
Carga pagina de whatsapp y espera a que cargue cumpliendo una condicion
"""
def load_WhatsApp(browser,settings,page_timeout):
    XPATH_WHATSAPP_READY = "//div[@class='_2Uo0Z']"
    browser.get(settings['url'])
    WebDriverWait(browser, page_timeout).until(EC.visibility_of_element_located((By.XPATH, XPATH_WHATSAPP_READY)))
    return True


"""
lee contactos de whatsapp
"""
def get_WhatsApp_Contacts(browser):
    XPATH_WHATSAPP_CONTACT = "//div[@class='_2wP_Y']" 
    XPATH_WHATSAPP_CONTACT_TEXT = ".//span[@class='_1wjpf']"
    contacts = []
    elements = browser.find_elements_by_xpath(XPATH_WHATSAPP_CONTACT)
    if elements and len(elements)>0:
        for e in elements:
            contact_name = e.find_element_by_xpath(XPATH_WHATSAPP_CONTACT_TEXT).text
            contacts.append({ 'name' : contact_name, 'element' : e })
    return contacts


"""
Activa chat de un contacto y valida que el nombre del chat coincida con el del contacto.
Esta funcion es bloqueante por el tiempo que se especifique en timeout si se excede este valor regresa false sino true
"""
def activate_WhatsApp_Contact_Chat(browser, page_timeout, contact):
    contact['element'].click()
    time.sleep(5)
    return True


"""
lee mensajes de un chat activo
"""
def get_WhatsApp_Chat_Messages(browser):
    results = []
    message_type = None
    message_direction = None
    message_text = None
    message_timestamp = None

    _XPATH_MESSAGES_ROOT = "//div[@class='{}']".format("_9tCEa")
    _XPATH_MESSAGES_ALL = ".//div[@class='{}' or @class='{}' or @class='{}']".format("vW7d1 _3rjxZ","vW7d1 _1nHRW","vW7d1")
    _XPATH_MESSAGES_TEXT = ".//div[@class='{}' or @class='{}' or @class='{}' or @class='{}']".format("_3_7SH _3DFk6 message-in tail","_3_7SH _3DFk6 message-out tail","_3_7SH _3DFk6 message-in","_3_7SH _3DFk6 message-out")
    _XPATH_NOTIF_TEXT = ".//div[@class='{}' or @class='{}' or @class='{}']".format("_3_7SH Zq3Mc","_3_7SH _14b5J Zq3Mc tail","_3_7SH Zq3Mc _37i-Z")
    _XPATH_MESSAGE_TEXT = ".//span[@class='{}']".format("selectable-text invisible-space copyable-text")
    _XPATH_MESSAGE_TIMESTAMP = ".//span[@class='{}']".format("_3EFt_")

    messages_root = browser.find_element_by_xpath(_XPATH_MESSAGES_ROOT)
    messages_and_notifys = messages_root.find_elements_by_xpath(_XPATH_MESSAGES_ALL)

    # iterate
    for msg in messages_and_notifys:
        class_name = msg.get_attribute("class")
        if class_name == 'vW7d1 _3rjxZ': # notificacion
            message_text = msg.find_element_by_xpath(_XPATH_NOTIF_TEXT).text
            results.append({'type':'notification', 'message': message_text})
        elif class_name in ('vW7d1 _1nHRW', 'vW7d1'): # messages
            chat_message = msg.find_element_by_xpath(_XPATH_MESSAGES_TEXT)
            class_name_msg = chat_message.get_attribute("class")
            message_direction = "recibido" if ("-in" in class_name_msg) else "enviado"
            message_text = chat_message.find_element_by_xpath(_XPATH_MESSAGE_TEXT).text
            message_timestamp = chat_message.find_element_by_xpath(_XPATH_MESSAGE_TIMESTAMP).text
            results.append({'type':'message','direction':message_direction, 'timestamp':message_timestamp, 'message': message_text})
    return results


"""
recorre contactos activando sus chats uno a uno y leyendo sus mensajes
"""
def get_WhatsApp_Contacts_Messages(browser,contacts):
    results = []
    if contacts and len(contacts)>0:
        for contact in contacts:
            activate_WhatsApp_Contact_Chat(browser,2,contact)
            messages = get_WhatsApp_Chat_Messages(browser)
            if messages and len(messages)>0:
                results.append({'contact_name':contact['name'], 'messages':messages})
    return results


"""
Main 
"""
def main():
    pass


"""
Si este script se llama directamente se invoca metodo main
"""
if __name__ == '__main__':
    main()