from getpass import getpass as g
from time import sleep
from selenium.webdriver.common.keys import Keys
import os
import requests
import bs4


def user_info(): # Retrieves username and password
    print('USERNAME:')
    usr = input('>>>')
    print('PASSWORD:')
    pw = g('>>>')
    return usr, pw


def login_page(driver, username, password):
    driver.get('https://mydramalist.com/signin')
    driver.find_element_by_xpath(
        '//*[@id="content"]/div/div[2]/div/div/div/div[1]/div/div/form/div[2]/input').send_keys(username)
    driver.find_element_by_xpath(
        '//*[@id="content"]/div/div[2]/div/div/div/div[1]/div/div/form/div[3]/input').send_keys(password)
    sleep(0.5)
    driver.find_element_by_xpath(
        '//*[@id="content"]/div/div[2]/div/div/div/div[1]/div/div/form/div[5]/div/div[1]/button').click()
    sleep(0.5)


def login_fail(driver):
    if driver.current_url == 'https://mydramalist.com/signin':
        logged_in = False
        print('!!Incorrect email or password!!')
        username, password = user_info()
        print("Attempting to login again")
    else:
        logged_in = True
        username = False
        password = False
        print("Successfully logged in")
    return username, password, logged_in


def directory(py_dir=os.getcwd()):
    if not os.path.exists('{}\\logs'.format(py_dir)):
        os.makedirs('{}\\logs'.format(py_dir))  # Create directory to store log files of the different series
    else:
        pass


def links(title):  # Searches for MDL link. Search term has to be accurate
    # Gets MDL link
    link_res = requests.get('https://mydramalist.com/search?q={}'.format(title))
    link_soup = bs4.BeautifulSoup(link_res.text, 'lxml')
    link = 'https://mydramalist.com{}'.format(link_soup.find('h6').contents[0]['href'])
    root = '{}/episode/'.format(link)

    # Gets Wikipedia link
    wiki_res = requests.get(link)
    wiki_soup = bs4.BeautifulSoup(wiki_res.text, 'lxml')
    native_title = wiki_soup.find('b', text='Native Title:').next_sibling.next_sibling.text
    query = native_title + 'site:ja.wikipedia.org'
    wiki_link = [link for link in search(query, lang='jp', start=0, stop=1, pause=0.1)][0]

    return root, wiki_link