from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import tkinter as tk
import time
import threading
from tkinter import font
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


options = Options()
options.add_argument("--start-maximized")

driver = None
index = 0
stop_flag = False
th = None

def visit_all_links():
    global driver
    global index
    global stop_flag

    while not stop_flag:
        with open('./keywords.txt', 'r') as f:
            keywords = [line.strip() for line in f]

        with open('./ignore_websites.txt', 'r') as f:
            ignore_websites = [line.strip() for line in f]

        i = 0
        for keyword in keywords:
            if i < index:
                i += 1
                continue

            if stop_flag:
                break

            driver = webdriver.Chrome(options=options)
            driver.get("https://www.google.com/search?q=" + keyword)
            time.sleep(5)

            links = driver.find_elements(by=By.XPATH, value='//a[@jsname = "UWckNb"]')

            valid_links = []
            for link in links:
                url = link.get_attribute('href')
                if not any(website in url for website in ignore_websites):
                    valid_links.append(url)

            for link_url in valid_links:
                try:
                    driver.execute_script(f"window.open('" + link_url + "', '__blank__');")
                    time.sleep(2)
                    try:
                        captcha_element = driver.find_element(by=By.ID, value="real_captcha_id")
                    except:
                        captcha_element = None

                    if captcha_element != None:
                        print('here')
                        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[starts-with(@name, 'a-') and starts-with(@src, 'https://www.google.com/recaptcha')]")))

                        # Clicking on element
                        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.recaptcha-checkbox-checkmark"))).click()
                        time.sleep(10)
                    time.sleep(2)
                except:
                    print("Website load failed")
                
            index += 1
            driver.quit()

def start_crawling():
    global stop_flag
    global index
    stop_flag = False
    index = 0
    threading.Thread(target=visit_all_links).start()

def pause_crawling():
    global stop_flag
    stop_flag = True

def resume_crawling():
    global stop_flag
    stop_flag = False
    threading.Thread(target=visit_all_links).start()

def add_keyword():
    text = input_keyword.get()
    with open('./keywords.txt', "a") as f:
        f.write(text + '\n')

def add_ignore():
    text = input_ignore.get()
    with open('./ignore_websites.txt', "a") as f:
        f.write(text + '\n')

root = tk.Tk()
root.title("Selenium GUI")
# root.geometry('1200x300')
root.configure(bg="lightblue", pady=10, padx=5)

# Create a custom font for the Entry widget
custom_font = font.nametofont("TkDefaultFont")
custom_font.configure(size=16)  # Set the font size as desired

keyword_label = tk.Label(root, text="Keyword", bg="lightblue", width=12, height=2)  # Set the background color of the label
input_keyword = tk.Entry(root, bg="lightgrey", width=40, font=custom_font)
ignore_label = tk.Label(root, text="Ignore", bg="lightblue", width=12, height=2)  # Set the background color of the label
input_ignore = tk.Entry(root, bg="lightgrey", width=40, font=custom_font)
start_button = tk.Button(root, text="Start", command=start_crawling, bg="green", width=12, height=2, cursor="hand2")
pause_button = tk.Button(root, text="Pause", command=pause_crawling, bg="orange", width=12, height=2, cursor="hand2")
resume_button = tk.Button(root, text="Resume", command=resume_crawling, bg="lightcoral", width=12, height=2, cursor="hand2")
add_button = tk.Button(root, text="Add Keyword", command=add_keyword, bg="lightgreen", width=12, height=2, cursor="hand2")
ignore_button = tk.Button(root, text="Add Ignore", command=add_ignore, bg="lightgreen", width=12, height=2, cursor="hand2")

keyword_label.grid(row=0, column=0, columnspan=1, padx=10, pady=5)
input_keyword.grid(row=0, column=2, columnspan=2, padx=10, pady=5, ipadx=20, ipady=10)
add_button.grid(row=0, column=7, columnspan=3, padx=5, pady=5)
ignore_label.grid(row=1, column=0, columnspan=1, padx=10, pady=5)
input_ignore.grid(row=1, column=2, columnspan=2, padx=10, pady=5, ipadx=20, ipady=10)
ignore_button.grid(row=1, column=7, columnspan=3, padx=5, pady=5)
start_button.grid(row=2, column=1, columnspan=2, padx=10, pady=5)
pause_button.grid(row=2, column=3, columnspan=2, padx=10, pady=5)
resume_button.grid(row=2, column=5, columnspan=2, padx=10, pady=5)

root.mainloop()
