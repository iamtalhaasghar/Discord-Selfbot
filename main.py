from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import time
import sys
import os
import platform
import multiprocessing
import atexit

# Variables
login_email = "email@email.com"
login_pass = "password"
login_username = "username"
chromepath = "chromedriver.exe"

process_list = []
imhuman = 0
selected_server = ""
selected_channel = ""


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(executable_path=chromepath, options=chrome_options)
driver.maximize_window()


helpmenu = """
---------------------
COMMAND USAGE                                   | COMMAND DESCRIPTION
# Basic Commands

help                                            | print out this message
exit                                            | shutdown bot
screenshot                                      | gets screenshot from driver and save it to same directory

# Server interactions

join SERVERURLORCODE                            | Joins to server
server SERVERID                                 | Switches to specified server
channel CHANNELID                               | Switched to specified channel
sendchannelmessage MESSAGE                      | Send message to specified channel (supports space in message)
sendchannelmessageloop COUNT COOLDOWN MESSAGE   | Send message to specified channel (COOLDOWN : can be int or float (1 or 0.5), supports space in message)
readchannelmessage                              | Read latest messages from server

# User interactions

allfriends                                      | List all friends
onlinefriends                                   | List all online friends
waitingfriends                                  | List all waiting friend requests
blockedfriends                                  | List all blocked friends
addfriend USERNAME#1234                         | add user as your friend
checkformessages                                | Check for new messages from friends
sendusermessage USERNAME#1234                   | Send message to user

---------------------
"""

# ETC Functions

def killdriver():
    driver.quit()

def senddirectkeys(TEXT):
    actions = ActionChains(driver)
    actions.send_keys(TEXT)
    actions.perform()

def clearscrn():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    
def returntohome(force):
    if force == True:
        driver.get("https://discord.com/channels/@me")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[aria-controls='ADD_FRIEND-tab']")))
    else:
        if driver.current_url != "https://discord.com/channels/@me":
            driver.get("https://discord.com/channels/@me")
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[aria-controls='ADD_FRIEND-tab']")))

def checkformsg():
    try:
        messages = driver.find_elements_by_css_selector("div.wrapper-1BJsBx")
        try:
            driver.find_elements_by_css_selector("lowerBadge-29hYVK")
            for element in messages:
                href = element.get_attribute('href')
                if "@me/" in href:
                    aria_label = element.get_attribute("aria-label")
                    print("[i] New message from " + aria_label)
                    print("[i] Reading chat ...")
                    driver.get("https://discord.com" + href)
                    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.contents-2mQqc9")))
                    try:
                        history = ""
                        msg = driver.find_elements_by_css_selector("div.contents-2mQqc9")
                        for index in msg:
                            history = history + "\n" + index.text
                        history = history.split(aria_label)
                        lastmsgs = history[-1:]
                        print(lastmsgs[0])
                        try:
                            driver.find_element_by_css_selector("button.barButtonAlt-mYL1lj.barButtonBase-2uLO1z").click()
                        except:
                            print("[!] Error while \"mark as read\" process")
                            pass
                        replyornot = input("[?] Do you want to reply? (Y/n)")
                        if replyornot == "" or replyornot == "Y" or replyornot == "y":
                            msgtosend = input("[?] Your message :")
                            driver.find_element_by_css_selector("div.markup-2BOw-j.slateTextArea-1Mkdgw.fontSize16Padding-3Wk7zP").send_keys(msgtosend + Keys.ENTER)
                            print("Sent!")
                    except Exception as e:
                        print(e)
                        pass
        except:
            print("No new message(s)")
            pass
    except:
        pass
    returntohome(False)


# LOGIN FUNCTIONS
def login():
    good2go = 0
    driver.get("https://discord.com/login")
    try:
        driver.find_element_by_name("email")
        good2go = 1
    except:
        print("[!] Couldn't locate \"email\" input")
        pass
    if good2go == 1:
        driver.find_element_by_name("email").send_keys(login_email)
        driver.find_element_by_name("password").send_keys(login_pass)
        driver.find_element_by_class_name("button-3k0cO7").click()
        time.sleep(2)
        if "Login or password is invalid." in driver.find_element_by_tag_name("body").text:
            print("Login or password is invalid.")
            return 0
        else:
            WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.container-3baos1")))
            source = driver.find_element_by_tag_name("body").text
            if login_username in source:
                print("[i] Login Successfull")
                return 1
            else:
                print("[!] Login Failed")
                return 0
    else:
        print("[!] Login Failed")
        return 0


def loginimhuman():
    global imhuman
    global driver
    driver = webdriver.Chrome(executable_path=chromepath)
    driver.maximize_window()
    driver.get("https://discord.com/login")
    driver.find_element_by_name("email").send_keys(login_email)
    driver.find_element_by_name("password").send_keys(login_pass)
    driver.find_element_by_class_name("button-3k0cO7").click()
    input("[i] Press \"Enter\" when login process over")
    source = driver.find_element_by_tag_name("body").text
    if login_username in source:
        print("[i] Login Successfull")
        imhuman = 1
    else:
        print("[!] Login Failed")
        imhuman = 0


# SERVER FUNCTIONS
def joinserver(joincode):
    driver.find_element_by_class_name("circleIconButton-jET_ig").click()
    time.sleep(1.5)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.footerButton-ayFTfX.button-38aScr.lookFilled-1Gx00P.colorGrey-2DXtkV.sizeMedium-1AC_Sl.sizeMedium-1AC_Sl"))).click()
    driver.find_element_by_css_selector("input.inputDefault-_djjkz.input-cIJ7To.inputInner-2akrSS").send_keys(joincode)
    driver.find_element_by_css_selector("button.button-38aScr.lookFilled-1Gx00P.colorBrand-3pXr91.sizeMedium-1AC_Sl.grow-q77ONN").click()

# USER FUNCTIONS
def addfriend(friendname):
    friendname = friendname[1:]
    returntohome(False)
    time.sleep(5)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[aria-controls='ADD_FRIEND-tab']"))).click()
    driver.find_element_by_css_selector("input.addFriendInput-4bcerK").send_keys(friendname + Keys.ENTER)
    time.sleep(1)
    try:
        print("[!]", driver.find_element_by_css_selector("div.colorStandard-2KCXvj.size16-1P40sf.body-Mj9Oxz").text)
    except:
        print("[i] Friend request sent !")
        pass
    
def allfriends():
    returntohome(False)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[aria-controls='ALL-tab']"))).click()
    for i in driver.find_elements_by_css_selector("div.peopleListItem-2nzedh"):
        print("Username    :" + i.text.split("\n")[0])
        print("Description :" + i.text.split("\n")[1])
        print("--")

def onlinefriends():
    returntohome(False)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[aria-controls='ONLINE-tab']"))).click()
    for i in driver.find_elements_by_css_selector("div.peopleListItem-2nzedh"):
        print("Username    :" + i.text.split("\n")[0])
        print("Description :" + i.text.split("\n")[1])
        print("--")

def waitingfriends():
    returntohome(False)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[aria-controls='PENDING-tab']"))).click()
    for i in driver.find_elements_by_css_selector("div.peopleListItem-2nzedh"):
        print("Username    :" + i.text.split("\n")[0])
        print("Description :" + i.text.split("\n")[1])
        print("--")

def sendusermessage(USERNAME):
    MESSAGE = input("Message :")
    returntohome(False)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.searchBarComponent-32dTOx"))).click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.input-2VB9rf"))).send_keys(USERNAME[1:])
    driver.find_element_by_css_selector("input.input-2VB9rf").send_keys(Keys.ENTER)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.markup-2BOw-j.slateTextArea-1Mkdgw.fontSize16Padding-3Wk7zP"))).send_keys(MESSAGE + Keys.ENTER)

# SERVER FUNCTIONS


def switchtoserver(SERVERID):
    global selected_server
    selected_server = SERVERID
    
def switchtochannel(CHANNELID):
    global selected_channel
    global selected_server
    selected_channel = CHANNELID
    driver.get("https://discord.com/channels/" + selected_server + "/" + selected_channel)
    
def sendchannelmessage(MESSAGE):
    global selected_channel
    global selected_server
    if selected_server != "" and selected_channel != "":
        url = driver.current_url
        if url != "https://discord.com/channels/" + selected_server + "/" + selected_channel:
            switchtochannel(selected_channel)
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.markup-2BOw-j.slateTextArea-1Mkdgw.fontSize16Padding-3Wk7zP"))).send_keys(MESSAGE + Keys.ENTER)
            print("Sent !")
        else:
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.markup-2BOw-j.slateTextArea-1Mkdgw.fontSize16Padding-3Wk7zP"))).send_keys(MESSAGE + Keys.ENTER)
            print("Sent !")
    else:
        print("Please Specify server and channel !")
            
def sendchannelmessageloop(COUNT, COOLDOWN, MESSAGE):
    global selected_channel
    global selected_server
    COUNT = int(COUNT)
    if "." in COOLDOWN:
        COOLDOWN = float(COOLDOWN)
    else:
        COOLDOWN = int(COOLDOWN)
    if selected_server != "" and selected_channel != "":
        url = driver.current_url
        if url != "https://discord.com/channels/" + selected_server + "/" + selected_channel:
            switchtochannel(selected_channel)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.markup-2BOw-j.slateTextArea-1Mkdgw.fontSize16Padding-3Wk7zP")))
        while True:
            if COUNT != 0:
                driver.find_element_by_css_selector("div.markup-2BOw-j.slateTextArea-1Mkdgw.fontSize16Padding-3Wk7zP").send_keys(MESSAGE + Keys.ENTER)
                time.sleep(COOLDOWN)
                COUNT -= 1
            else:
                break
    else:
        print("Please Specify server and channel !")

def readchannelmessage():   
    global selected_server
    global selected_channel
    if selected_server != "" and selected_channel != "": 
        if driver.current_url != "https://discord.com/channels/" + selected_server + "/" + selected_channel:    
            switchtochannel(selected_channel)   
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.message-2qnXI6.cozyMessage-3V1Y8y.groupStart-23k01U.wrapper-2a6GCs.cozy-3raOZG.zalgo-jN1Ica")))
            msgs = driver.find_elements_by_css_selector("div.message-2qnXI6.cozyMessage-3V1Y8y.groupStart-23k01U.wrapper-2a6GCs.cozy-3raOZG.zalgo-jN1Ica")
            for msg in msgs:
                print(": Message Start :\n" + msg.text + "\n: Message End :\n")
        else:
            msgs = driver.find_elements_by_css_selector("div.message-2qnXI6.cozyMessage-3V1Y8y.groupStart-23k01U.wrapper-2a6GCs.cozy-3raOZG.zalgo-jN1Ica")
            for msg in msgs:
                print(": Message Start :\n" + msg.text + "\n: Message End :\n")
    else:
        print("Please Specify server and channel !")
        
# MAIN FUNCTION

def main():
    while True:
        whattodo = input("==>")
        if " " in whattodo:
            whattodo = whattodo.split(" ")
            if whattodo[0] == "join":
                joinserver(whattodo[1])
            elif whattodo[0] == "addfriend":
                friendname = ""
                for index in whattodo[1:]:
                    friendname = friendname + " " + index
                addfriend(friendname)
            elif whattodo[0] == "server":
                switchtoserver(whattodo[1])
                print("Server set to :", whattodo[1])
            elif whattodo[0] == "channel":
                switchtochannel(whattodo[1])
                print("Channel set to :", whattodo[1])
            elif whattodo[0] == "sendchannelmessage":
                message = ""
                for index in whattodo[1:]:
                    message = message + " " + index
                sendchannelmessage(message)
            elif whattodo[0] == "sendchannelmessageloop":
                message = ""
                for index in whattodo[3:]:
                    message = message + " " + index
                sendchannelmessageloop(whattodo[1], whattodo[2], message)
            elif whattodo[0] == "sendusermessage":
                username = ""
                for index in whattodo[1:]:
                    username = username + " " + index
                sendusermessage(username)
        else:
            if whattodo == "screenshot":
                driver.save_screenshot("ScreenShot.png")
            elif whattodo == "exit":
                killdriver()
                break
            elif whattodo == "help":
                print(helpmenu)
            elif whattodo == "allfriends":
                allfriends()
            elif whattodo == "onlinefriends":
                onlinefriends()
            elif whattodo == "waitingfriends":
                waitingfriends()
            elif whattodo == "checkformessages":
                checkformsg()
            elif whattodo == "readchannelmessage":
                readchannelmessage()




if __name__ == "__main__":
    atexit.register(killdriver)
    while True:
        clearscrn()
        print("---------------------------* Kral4's Discord Selfbot *---------------------------")
        print("Logging in ...")
        if login() == 1:
            break
        elif imhuman == 1:
            break
        else:
            retry = 0
            print("an problem occured while trying to login discord, migth be \"are you human test\"")
            retry = input("Retry (Y/n)")
            if retry == "":
                retry = 1
            elif retry == "Y" or retry == "y":
                retry = 1
            elif retry == "N" or retry == "n":
                retry = 0
            if retry != 1:
                choice = 0
                choice = input("Do you want to proceed with \"let me do human test\" function (Y/n)")
                if choice == "":
                    choice = 1
                elif choice == "Y" or choice == "y":
                    choice = 1
                elif choice == "N" or choice == "n":
                    choice = 0
                if choice == 1:
                    killdriver()
                    loginimhuman()
                    break
                else:
                    sys.exit(0)
    print("Type \"help\" for command list")     
    main()
