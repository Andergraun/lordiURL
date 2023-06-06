import re

import requests

import base64

import html

import threading

import os

import platform

from bs4 import BeautifulSoup

from urllib.parse import unquote, urlsplit, urlunsplit, urlparse

def get_string(string_key, language):

    if language == "ru":

        return RUSSIAN_STRINGS.get(string_key, "")

    elif language == "en":

        return ENGLISH_STRINGS.get(string_key, "")

    else:

        return ""

def decode_percent_encoding(encoded_url):

    return unquote(encoded_url)

def decode_base64_encoding(encoded_url):

    try:

        return base64.urlsafe_b64decode(encoded_url).decode()

    except:

        return None

def decode_punycode_encoding(encoded_url):

    try:

        scheme, netloc, path, query, fragment = urlsplit(encoded_url)

        decoded_netloc = '.'.join([x.decode('idna') for x in netloc.split('.')])

        return urlunsplit((scheme, decoded_netloc, path, query, fragment))

    except:

        return None

def decode_html_entities(encoded_url):

    return html.unescape(encoded_url)

def decode_rot13(encoded_url):

    try:

        return encoded_url.translate(

            str.maketrans("ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",

                          "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm"))

    except:

        return None

def find_encoded_urls(url, depth=1):

    if depth < 0:

        return

    parsed_url = urlparse(url)

    if not parsed_url.scheme:

        url = "https://" + url

    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    page_title = soup.find('title')

    if page_title:

        print(f"Заголовок | Header (title): {page_title.text}")

    strategies = [

        ("Percent encoding", r"(?:%[0-9A-Fa-f]{1,2})+", decode_percent_encoding),

        ("Base64 encoding", r"(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)", decode_base64_encoding),

        ("Punycode encoding", r"xn--[0-9a-z]+(?:\.[a-z]+)+", decode_punycode_encoding),

        ("HTML entities", r"&[a-zA-Z0-9]+;", decode_html_entities),

        ("ROT13", r"(?:[a-zA-Z])+?(?:s)?", decode_rot13)

    ]

    results = []

    for title, pattern, decode_func in strategies:

        encoded_urls = re.findall(pattern, str(soup))

        decoded_urls = [(e_url, decode_func(e_url)) for e_url in encoded_urls]

        for e_url, d_url in decoded_urls:

            if d_url and d_url != e_url and len(d_url) > 5:

                result = f"{title}: {e_url} --> {d_url}"

                results.append(result)

                print(result)

                find_encoded_urls(d_url, depth - 1)

    return results

    

def run_with_timeout(func, args, timeout):

    result_container = []

    def wrapper():

        result_container.append(func(*args))

    thread = threading.Thread(target=wrapper)

    thread.start()

    thread.join(timeout)

    return result_container[0] if len(result_container) > 0 else None

def clear_console():

    if platform.system().lower() == "windows":

        os.system("cls")

    else:

        os.system("clear")

def main_loop():

    language = input("Выберите язык | Choose language (ru/en): ").lower()

    while language not in ("ru", "en"):

        language = input("Выберите язык (ru/en): ").lower()

    while True:

        command = input(get_string("ENTER_URL", language)).lower()

        

        if command == "выход" or command == "exit":

            break

        elif command == "очистить" or command == "clear":

            clear_console()

            continue

        

        url = command

        

        depth = int(input(get_string("ENTER_DEPTH", language)))

        print(get_string("SEARCH_DECODE", language))

        results = run_with_timeout(find_encoded_urls, (url, depth), 15)

        if results is None:

            print(get_string("TIMEOUT", language))

RUSSIAN_STRINGS = {

    "ENTER_URL": "Telegram • @LordiHub   Введите URL сайта или 'выход' для завершения: ",

    "ENTER_DEPTH": "Введите глубину поиска (например, 1 или 2): ",

    "SEARCH_DECODE": "Поиск и декодирование URL-ов:",

    "INVALID_URL": "Похоже вы неправильно написали адрес :(",

    "TIMEOUT": "Превышено время ожидания результатов (15 секунд)"

}

ENGLISH_STRINGS = {

    "ENTER_URL": "Telegram • @LordiHub Enter the website URL or 'exit' to quit: ",

    "ENTER_DEPTH": "Enter the search depth (e.g., 1 or 2): ",

    "SEARCH_DECODE": "Searching and decoding URLs:",

    "INVALID_URL": "It seems you entered an incorrect address :(",

    "TIMEOUT": "Time limit exceeded for results (15 seconds)"

}

if __name__ == "__main__":

    main_loop()

    url = input("Введите URL сайта: ")

    depth = int(input("Введите глубину поиска (например, 1 или 2): "))

    print("Поиск и декодирование URL-ов:")

    find_encoded_urls(url, depth)
