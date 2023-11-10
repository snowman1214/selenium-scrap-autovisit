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

index = 0
stop_flag = False
th = None

with open('./proxy.txt', 'r') as f:
    proxys = [line.strip() for line in f]

c_proxy = proxys[0]

def change_proxy():
    global c_proxy
    with open('./proxy.txt', 'r') as f:
        proxys = [line.strip() for line in f]
    temp_proxy = proxys[0]
    for i in range(0, len(proxys) - 2):
        proxys[i] = proxys[i + 1]
    proxys[len(proxys) - 1] = temp_proxy
    f.close()
    with open('./proxy.txt', 'w') as f:
        for proxy in proxys:
            f.write(proxy + '\n')
    f.close()
    c_proxy = proxys[0]
    
def visit_all_links():
    global index
    global stop_flag
    global th
    global c_proxy
    driver = None
    while not stop_flag:
        with open('./ignore_websites.txt', 'r') as file_ignore:
            ignore_websites = [line.strip() for line in file_ignore]
        with open('./keywords.txt', 'r') as file_keyword:
            texts = [line.strip() for line in file_keyword]
            temp_texts = texts
        for length in range(0, len(texts) - 1):
            temp_texts[length] = texts[length] + '\n'
        i = 0
        for text in texts:
            if i < index:
                i += 1
                continue

            if stop_flag:
                driver.quit()
                break
            result = text.split(',')
            keyword = result[0]
            keyword_search_count = int(result[1])
            keyword_max_count = int(result[2])
            keyword_current_count = int(result[3])
            
            # options.add_argument(f'--proxy-server={c_proxy}')
            driver = webdriver.Chrome(options=options)
            driver.get("https://www.google.com/search?q=" + keyword)
            time.sleep(5)

            links = driver.find_elements(by=By.XPATH, value='//a[@jsname = "UWckNb"]')

            valid_links = []
            link_count = 0
            for link in links:
                url = link.get_attribute('href')
                if not any(website in url for website in ignore_websites):
                    if link_count == keyword_search_count:
                        break
                    valid_links.append(url)
                    link_count += 1 

            for link_url in valid_links:
                link_url = 'https://www.babla.ru/%D0%B0%D0%BD%D0%B3%D0%BB%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D0%B9-%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9/puppy'
                try:
                    driver.execute_script(f"window.open('" + link_url + "', '__blank__');")
                    time.sleep(0.5)
                    try:
                        captcha_element = driver.find_element(by=By.ID, value="challenge-stage")
                    except NoSuchElementException:
                        captcha_element = None
                    # print(captcha_element)
                    if captcha_element:
                        print('here')
                        driver.quit()
                        return
                    #     # visit_all_links()
                    time.sleep(2)
                except:
                    print("Website load failed")
            temp_texts[index] = keyword + ',10,1500,' + str(keyword_current_count + 1) + '\n'
            with open('./keywords.txt', 'w') as file_keyword:
                file_keyword.writelines(temp_texts)
            index += 1
            i += 1
            time.sleep(2)
            driver.quit()
        break

def start_crawling():
    global stop_flag
    global index
    global th
    stop_flag = False
    index = 0
    th = threading.Thread(target=visit_all_links)
    th.start()

def pause_crawling():
    global stop_flag
    stop_flag = True

def resume_crawling():
    global stop_flag
    stop_flag = False
    global th
    th = threading.Thread(target=visit_all_links)
    th.start()

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