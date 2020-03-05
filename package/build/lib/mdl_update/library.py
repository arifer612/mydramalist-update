from getpass import getpass as g
from googlesearch import search
import os
import requests
import bs4


def user_info(): # Retrieves username and password
    print('USERNAME:')
    usr = input('>>>')
    print('PASSWORD:')
    pw = g('>>>')
    return usr, pw


def login(session, username, password):
    return session.post('https://mydramalist.com/signin', data=login_payload(username,password))


def login_fail(response):
    try:
        token = response.request.headers['Cookie'].split(';')[1].split('=')[1]
        logged_in = True
        username = False
        password = False
    except Exception:
        token = ''
        logged_in = False
        print('!!Incorrect email or password!!')
        username, password = user_info()
        print("Attempting to login again")
    return username, password, logged_in, token


def directory(py_dir=os.getcwd()):
    if not os.path.exists('{}\\logs'.format(py_dir)):
        os.makedirs('{}\\logs'.format(py_dir))  # Create directory to store log files of the different series
    else:
        pass


def links(title):  # Searches for MDL link. Search term has to be accurate
    # Gets MDL link
    link_res = requests.get('https://mydramalist.com/search',params={'q':title})
    link_soup = bs4.BeautifulSoup(link_res.text, 'lxml')
    link = 'https://mydramalist.com{}'.format(link_soup.find('h6').contents[0]['href'])
    root = '{}/episode/'.format(link)

    # Gets Wikipedia link
    wiki_res = requests.get(link)
    wiki_soup = bs4.BeautifulSoup(wiki_res.text, 'lxml')
    try:
        native_title = wiki_soup.find('b', text='Native Title:').next_sibling.next_sibling.text
    except AttributeError:
        native_title = wiki_soup.find(attrs={'itemprop':'name'}).text
    query = native_title + ' site:ja.wikipedia.org'
    wiki_link = [link for link in search(query, lang='jp', start=0, stop=1, pause=0.1)][0]

    return native_title, root, wiki_link


def login_payload(username,password):
    return {
    'username': username,
    'password': password
}


def update_payload(wiki_link,date,additional_info=None):
    return {
    'category':'details',
    'notes':'Information from {}{}'.format(wiki_link,' '+additional_info if additional_info else ''),
    'release_date':date
}


def update_link(id,token):
    return 'https://mydramalist.com/v1/edit/episodes/{}/details?lang=undefined&token={}'.format(id,token)