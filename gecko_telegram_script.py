import requests
import time
from bs4 import BeautifulSoup
import re
import os
from model import Coins
from model import Coin
from telegram_send import send
import json
import threading
import sys

##############################################################################################
# POMOŽNE FUNKCIJE
##############################################################################################

def krepko(niz):
    return f'\033[01m{niz}\033[0m'
def modro(niz):
    return f'\033[1;94m{niz}\033[0m'
def rdece(niz):
    return f'\033[1;91m{niz}\033[0m'
def zeleno(niz):
    return f'\033[0;32m{niz}\033[0m'
def rumeno(niz):
    return f'\033[0;33m{niz}\033[0m'
def lightcyan(niz):
    return f'\033[0;96m{niz}\033[0m'
def pink(niz):
    return f'\033[0;95m{niz}\033[0m'
def lightgreen(niz):
    return f'\033[0;92m{niz}\033[0m'


def html_first_page(): #prekopira html strani iz coingeckona
    url = f"https://www.coingecko.com/en/coins/recently_added?page=1"
    odziv = requests.get(url)
    html = odziv.text
    soup = BeautifulSoup(html, features="html.parser")
    with open(f'recent_coins_page.html', 'w', encoding="utf-8") as f:
            print(soup, file=f)
    

def new_coins(): 
    coins = []
    with open(f"recent_coins_page.html", "r", encoding="utf-8") as f:
        vsebina = f.read()
        vzorec = (
    r'<a class="d-lg-none font-bold" href="/en/coins/(.+?)">'
    r'((.|\n)*?)'
    r'<td class="trade p-0 col-market pl-2 text-center">'
    r'(.|\n)*?'
    r'</td>'
    )
        for iteration in re.finditer(vzorec, vsebina):
            info = iteration[0].split("\n")
            blockchain = info[11].split('"')[3] #na kermo blockchaino je token
            name = info[0].split("/")[-1][:-2] #token name
            gecko_link = "https://www.coingecko.com/en/coins/" + name + "/"
            bought = False

            if blockchain == 'Binance Smart Chain':
                coin = Coin(name, gecko_link, bought)  
                if name not in shramba.coins_in_names: #dodaj sam tokene ko ž niso shrajeni
                    coins.append(coin) #dodaj coin če je na BSC
                    shramba.coins.append(coin)
                    shramba.coins_in_names[coin.name] = coin
                else:
                    pass        
    return coins


def no_CMC_urls(SEZNAM_COINOV): #vzame seznam coinov, vrne seznam coin url-jov ki niso na CMC
    NOV_SEZNAM = []
    for coin in SEZNAM_COINOV:
        request_response = requests.head(coin.cmc_link)
        time.sleep(0.5)
        code = request_response.status_code
        if code == 200:
            print(lightcyan(f"{coin.name} is listed on CMC"))
        elif code == 404:
            print(rumeno(f"{coin.name} is not yet listed on CMC"))
            NOV_SEZNAM.append(coin)
    return NOV_SEZNAM


def send_new_coins_on_telegram(coins):
    lista = "NOV COIN KO NI NA CMC:\n"

    if len(coins) > 0:
        for coin in coins:
            lista += coin.name + ": " + coin.gecko_link + "\n"
        send(messages = [lista])
    else:
        print(rdece(krepko("No new links available.")))


def send_cmc_coins_telegram(coins):
    lista = "PRŠO NA CMC:\n"
    if len(coins) > 0:
        for coin in coins:
            lista += coin.name + ": " + coin.gecko_link + "\n"
        send(messages = [lista])
    else:
        print(lightcyan("None of the bought coins have appeared on ") + lightcyan(krepko("CMC")) + lightcyan("."))


def remove_html_page():
    os.remove(f"recent_coins_page.html")


###########################################################################
# telegram
###########################################################################


TOKEN = "2130234948:AAGsFrHIK0oGbTQ6Aed7DvgaxqKfcafL06M"
URL = f"https://api.telegram.org/bot{TOKEN}/"


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf-8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates():
    url = URL + "getUpdates"
    js = get_json_from_url(url)
    return js


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def last_bought_coin():
    with open("telegram_msg.txt", "r", encoding="utf-8") as f:
        last_textchat = f.read().strip().split(",")
        print((lightgreen("last bought coin: ") + rumeno(krepko(last_textchat[0]))))


def new_coin_bought():
    with open("telegram_msg.txt", "r", encoding="utf-8") as f:
        last_textchat = f.read().strip().split(",")
        #print((lightgreen("last bought coin: ") + rumeno(krepko(last_textchat[0]))))

    text, chat = get_last_chat_id_and_text(get_updates())
    
    if (text, chat) != (last_textchat[0], int(last_textchat[1])):
        send_message("Zaka si pa stako smetje kupo bumbar??", chat)
        with open("telegram_msg.txt", "w") as f:
            print(text + "," + str(chat), file=f)
        print(rumeno(krepko(f"Julgor just bought: {text}")))
        return text
    else:
        return None


def add_bought_status_to_coin(text):
    if text != None:
        for coin in shramba.coins:
            if coin.name == text:
                coin.bought = True
    else:
        pass


def saved_coins_that_are_bought():
    return [coin for coin in shramba.coins if coin.bought == True]


def CMC_urls(SEZNAM_COINOV): #vzame seznam coinov, vrne seznam coin url-jov ki niso na CMC
    NOV_SEZNAM = []
    for coin in SEZNAM_COINOV:
        request_response = requests.head(coin.cmc_link)
        time.sleep(0.5)
        code = request_response.status_code
        if code == 200:
            NOV_SEZNAM.append(coin)
            coin.bought = "sold"
    return NOV_SEZNAM


###########################################################################
# NALOŽI SHRAMBO
###########################################################################


DATA = "shramba.json"

try:
    shramba = Coins.nalozi_stanje(DATA)
except FileNotFoundError:
    shramba = Coins()


###########################################################################
# run:
###########################################################################


def Gecko_cmc_storage_telegram_msg_update():
    while True:
        ############################################# PREVERI ČE JE KER OD KUPLENIH COINOV ŽE LISTAN NA CMC
        last_bought_coin()
        time.sleep(0.5)
        bought_coins = saved_coins_that_are_bought()
        cmc_listed = CMC_urls(bought_coins)
        send_cmc_coins_telegram(cmc_listed)
        #############################################
        
        ############################################# POGLEDA ČE JE KAK NOV COIN PRŠ NA GECKO, KO ŠE NI NA CMC. ČE SO, JIH DODA PA POŠLE TELEGRAM MSG Z LINKAM
        html_first_page()
        coins = new_coins()
        coins_not_on_cmc = no_CMC_urls(coins)
        send_new_coins_on_telegram(coins_not_on_cmc)
        shramba.shrani_stanje(DATA)
        time.sleep(0.5)
        remove_html_page()
        #############################################
        print(pink("2 min until next update...\n\n"))
        time.sleep(120)
    

def Telegram_msg_receiver():
    
    while True: 
        ############################################## ČE JE KDO NAPISAL TELEGRAM BOTU, DA JE KUPIL NOV COIN, TEMU COINU SPREMENI STATUS V KUPLJEN = TRUE
        new_coin = new_coin_bought()
        add_bought_status_to_coin(new_coin)
        time.sleep(0.5)
        ##############################################
    
if __name__ == '__main__':
    
    x = threading.Thread(target=Gecko_cmc_storage_telegram_msg_update)
    x.start()
    y = threading.Thread(target=Telegram_msg_receiver)
    y.start()
    
    
        

    

