import requests
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import sys
import shutil

ROOT = "./downloads/"
SCROLL_PAUSE_TIME = 0.5

def download_tiktok(tiktok, path="."):
    url = f"https://tdl.besecure.eu.org/api/download?url={tiktok}"
    dwn_id = tiktok.split('/')[-1]
    try:
        res = requests.get(url).json()
        dwn_link = res["video"]["urls"][0]
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(dwn_link, f"{path}/{dwn_id}.mp4")
    except Exception as e:
        print("error on download : {}\nID : {}\nFull link : {}\n{}".format(e, dwn_id, tiktok, res))
        time.sleep(2)

def initialize_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--no-capture")
    browser =  webdriver.Chrome(options=chrome_options)
    return browser

def scroll_to_bottom(browser):
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_video_links(user):
    links = []
    browser = initialize_selenium()
    try:
        browser.get(f'https://www.tiktok.com/{user}')
        time.sleep(4)
        scroll_to_bottom(browser)

        element = browser.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div[2]/div[2]/div");
        count = int(len(element.find_elements(By.XPATH, "//*[@class='tiktok-x6y88p-DivItemContainerV2 e19c29qe7']/div"))/2)
    except Exception as e:
        sys.stderr.write(f"Invalid account {user}")
        return []
    for a in range(1, count):
        try:
            video = browser.find_element(By.XPATH, f"/html/body/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[{a}]/div[1]/div/div/a")
            links.append(video.get_attribute("href"))
        except:
            pass
    browser.close()
    return links

def fuck_user(user):
    videos = get_video_links(user)
    dwn_path = f"{ROOT}{user}"
    if os.path.exists(dwn_path):
        shutil.rmtree(dwn_path)
    os.mkdir(dwn_path)
    count = 1
    count_videos = len(videos)
    for video in videos:
        print(f"Downloading video {count}/{count_videos}")
        download_tiktok(video, dwn_path)
        time.sleep(1.5)
        count+=1

def main(file_name):
    if not os.path.exists(ROOT):
        os.mkdir(ROOT)
    with open(file_name, 'r') as accounts:
        for account in accounts.readlines():
            fuck_user(account.rstrip())

if __name__ == "__main__":
    try:
        file_name = "accounts.txt" if len(sys.argv) <= 1 else sys.argv[1]
        main(file_name)
    except Exception as e:
        sys.stderr.write("An error occurred dm @0xCurtsi on Twitter : {}".format(e))
        