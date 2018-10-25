import sys
from util import *

def main():
    settings = load_settings("test.txt","my-config")
    if settings:
        browser = init_selenium(settings)
        if load_WhatsApp(browser,settings,page_timeout=30):
            contacts = get_WhatsApp_Contacts(browser)
            if contacts and len(contacts)>0:
                result = get_WhatsApp_Contacts_Messages(browser, contacts)
                if result:
                    if saveAsJSON(result,"output.json"):
                        print("All Done. File Saved !!")

if __name__ == '__main__':
    main()