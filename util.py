import sys
import json
import codecs
import configparser
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

# selector xpath de imagen de chat principal
XPATH_WHATSAPP_READY = "//div[@class='_2Uo0Z']" 

# selector xpath de cada contacto a la izquierda de la ventana
XPATH_WHATSAPP_CONTACT = "//div[@class='_2wP_Y']" 

# selector xpath que contiene nombre del contacto, parent = XPATH_WHATSAPP_CONTACT
XPATH_WHATSAPP_CONTACT_TEXT = ".//span[@class='_1wjpf']" 

# selector xpath que contiene el nombre del contacto al que pertenece el chat
XPATH_WHATSAPP_CHAT_TEXT = "//div[@class='_2zCDG']" 

# selectores xpath para divs de mensajes
XPATH_WHATSAPP_CHAT_MESSAGES = "//div[@class='_3_7SH _3DFk6 message-in tail'] | //div[@class='_3_7SH _3DFk6 message-out tail'] | //div[@class='_3_7SH _3DFk6 message-in'] | //div[@class='_3_7SH _3DFk6 message-out']"

# selector xpath para texto del mensaje
XPATH_WHATSAPP_CHAT_MESSAGE_TEXT = ".//span[@class='selectable-text invisible-space copyable-text']"

# selector xpath para marca de tiempo del mensaje
XPATH_WHATSAPP_CHAT_MESSAGE_TIMESTAMP = ".//span[@class='_3EFt_']"

"""
serializa objecto a json y lo guarda en un archivo
"""
def saveAsJSON(obj, file_name):
    try:
        success = False

        # serialize json
        json_output = json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))

        # save
        file = codecs.open(file_name, "w", "utf-8")
        file.write(json_output)
        file.close()

        success = True
    except:
        print ("saveAsJSON error:", sys.exc_info()[0])
        raise
    return success


"""
Carga datos de archivo de configuracion
"""
def load_settings(config_file, section_name):
    try:
        settings = None
        config_parser = configparser.RawConfigParser()
        config_file_path = config_file
        config_parser.read(config_file_path)

        settings = {
            'driver_path': config_parser.get(section_name, 'DRIVER_PATH'),
            'browser_profile': config_parser.get(section_name, 'BROWSER_PROFILE'),
            'url': config_parser.get(section_name, 'URL')
        }
    except:
        print ("load_settings error:", sys.exc_info()[0])
    return settings


"""
Inicializa selenium con chrome y settings correspondientes
"""
def init_selenium(settings,args=None):
    try:
        browser = None
        chrome_options = webdriver.ChromeOptions()
        
        if settings['browser_profile']:
            chrome_options.add_argument("user-data-dir=" + settings['browser_profile'])
        
        if args and len(args)>0:
            for arg in args:
                chrome_options.add_argument(arg)
        
        browser = webdriver.Chrome(executable_path=settings['driver_path'], chrome_options=chrome_options)
    except:
        print ("init_selenium error:", sys.exc_info()[0])
    return browser


"""
Carga pagina de whatsapp y espera a que cargue cumpliendo una condicion
"""
def load_WhatsApp(browser,settings,page_timeout):
    try:
        success = False
        browser.get(settings['url'])
        EC.text_to_be_present_in_element
        WebDriverWait(browser, page_timeout).until(EC.visibility_of_element_located((By.XPATH, XPATH_WHATSAPP_READY)))
        success = True
    except TimeoutException:
        print ("load_WhatsApp error:", sys.exc_info()[0])
    return success


"""
lee contactos de whatsapp
"""
def get_WhatsApp_Contacts(browser):
    try:
        contacts = []
        elements = browser.find_elements_by_xpath(XPATH_WHATSAPP_CONTACT)
        if elements and len(elements)>0:
            for e in elements:
                contact_name = e.find_element_by_xpath(XPATH_WHATSAPP_CONTACT_TEXT).text
                contacts.append({ 'name' : contact_name, 'element' : e })
        else:
            return None
    except:
        print ("get_WhatsApp_Contacts error:", sys.exc_info()[0])
        return None
    return contacts


"""
Activa chat de un contacto y valida que el nombre del chat coincida con el del contacto.
Esta funcion es bloqueante por el tiempo que se especifique en timeout si se excede este valor regresa false sino true
"""
def activate_WhatsApp_Contact_Chat(browser, page_timeout, contact):
    try:
        success = False
        contact['element'].click()
        WebDriverWait(browser, page_timeout).until(EC.text_to_be_present_in_element((By.XPATH, XPATH_WHATSAPP_CHAT_TEXT), contact['name']))
        success = True
    except TimeoutException:
        print ("activate_WhatsApp_Contact_Chat error:", sys.exc_info()[0])
    return success

"""
lee mensajes de un chat activo
"""
def get_WhatsApp_Chat_Messages(browser):
    try:
        results = []
        direction = None
        messages = browser.find_elements_by_xpath(XPATH_WHATSAPP_CHAT_MESSAGES)
        if messages and len(messages)>0:
            for message in messages:

                # mensaje enviado o recibido

                class_name = message.get_attribute("class")
                if "-in" in class_name:
                    direction = "recibido"
                elif "-out" in class_name:
                    direction= "enviado"
                else:
                    pass
                
                # texto del mensaje

                text = message.find_element_by_xpath(XPATH_WHATSAPP_CHAT_MESSAGE_TEXT).text

                # hora del mensaje

                timestamp = message.find_element_by_xpath(XPATH_WHATSAPP_CHAT_MESSAGE_TIMESTAMP).text

                results.append({'direction':direction, 'timestamp':timestamp, 'message': text})
        else:
            return None
    except:
        print ("get_WhatsApp_Chat_Messages error:", sys.exc_info()[0])
        return None
    return results


"""
recorre contactos activando sus chats uno a uno y leyendo sus mensajes
"""
def get_WhatsApp_Contacts_Messages(browser,contacts):
    try:
        results = []
        if contacts and len(contacts)>0:
            for contact in contacts:
                activate_WhatsApp_Contact_Chat(browser,2,contact)
                messages = get_WhatsApp_Chat_Messages(browser)
                if messages and len(messages)>0:
                    results.append({'contact_name':contact['name'], 'messages':messages})
    except:
        print ("get_WhatsApp_Contacts_Messages error:", sys.exc_info()[0])
        return None
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