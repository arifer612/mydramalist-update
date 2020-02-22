import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from googlesearch import search
import bs4
from time import sleep
from getpass import getpass as g


def user_info():
    print('USERNAME:')
    usr = input('>>>')
    print('PASSWORD:')
    pw = g('>>>')
    return usr, pw


def login(driver, username='', password=''): # Logs into MDL
    if driver and username and password:  # Check if non-empty
        def login_page(driver, username, password):
            driver.get('https://mydramalist.com/signin')
            driver.find_element_by_xpath(
                '//*[@id="content"]/div/div[2]/div/div/div/div[1]/div/div/form/div[2]/input').send_keys(username)
            driver.find_element_by_xpath(
                '//*[@id="content"]/div/div[2]/div/div/div/div[1]/div/div/form/div[3]/input').send_keys(password)
            driver.find_element_by_xpath(
                '//*[@id="content"]/div/div[2]/div/div/div/div[1]/div/div/form/div[5]/div/div[1]/button').click()

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

        logged_in = False
        attempts = 0
        while logged_in is False and attempts < 3:
            sleep(1)
            login_page(driver, username, password)
            username, password, logged_in = login_fail(driver)
            attempts += 1
        if attempts == 3:
            print("Please get the right account and password and try again later.")
            driver.quit()
            exit()
        else:
            pass
    else:
        print('Missing arguments')


def wiki(title): # Searches for wikipedia link. Search term has to be accurate
    query = title + ' wikipedia jp'
    wiki_link = [link for link in search(query, lang='jp', start=0, stop=1, pause=0.1)][0]
    return wiki_link


def search_for_title(title): # Searches for MDL link. Search term has to be accurate
    res = requests.get('https://mydramalist.com/search?q={}'.format(title))
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    link = soup.find('h6').contents[0]['href']
    root = 'https://mydramalist.com{}/episode/'.format(link)
    return root


def ep_list(title): # Generates a list with the episode numbers and its air dates
    page_src = requests.get(wiki(title))
    soup = bs4.BeautifulSoup(page_src.text, 'lxml')
    episode = dict()
    start_info = soup.find('th', text='放送期間').next_sibling.text.replace('\n','').split(' - ')[0]
    end_info = soup.find('th', text='放送期間').next_sibling.text.replace('\n','').split(' - ')[-1] # Force airing shows to return single = False
    start_year = start_info.split('年')[0]
    if '年' not in end_info: # Checks if series ends on the same year
        single = True
        year_list = [table for table in soup.find_all(attrs={'class': 'wikitable'}) for entry in table.tbody.tr.contents if '放送日' in entry]
    else:
        single = False
        year_list = soup.find_all(attrs={'class': 'NavFrame'})

    def extract_date_month(entry):
        month = entry.split('月')[0]
        date = entry.split('月')[1].split('日')[0]
        return date, month

    def extract_year(entry): # Only single = False will trigger the use of entry
        if single:
            year = start_year
        else:
            year = entry.div.text[:4]  # Extracts the year
        return year

    def extract_eps(entry):
        if single:
            table = entry.find_all('tr')[1:]  # [2:] to remove the first 2 entries which are summaries
        else:
            table = entry.find(attrs={'class':'wikitable'}).find_all('tr')[1:]
        return table

    def extract_ep_and_date(entry):  # Entry here is the 'tr' class
        dateinfo = [info for info in entry.contents]  # Extracts the date
        ep_num = dateinfo[1].text.replace('\n', '')
        date, month = extract_date_month(dateinfo[3].text)
        return ep_num, date, month

    def entry(i):
        return episode['{}'.format(i)].split(',')

    for year_entry in year_list:
        year = extract_year(year_entry)
        for ep in extract_eps(year_entry):
            ep_num, date, month = extract_ep_and_date(ep)
            info = '{},{},{}'.format(month, date, year)
            episode[ep_num] = info

    ep_list = []
    for i in range(1, len(episode)):
        ep_list.append([i, entry(i)])
    return ep_list


def seriesupdate(driver, root, update_list, wiki_link=''):
    # root : MyDramaList link to the series
    # update_list: may be shortened to remove already updated episodes by keeping comparing against a log file
    def link(i):
        return '{}{}'.format(root, i)

    def edit_page(day, month, year):
        sleep(1)
        month_button = driver.find_element_by_xpath(
            '//*[@id="details"]/form/div[4]/div/div/div/div[1]/div/div/input')
        day_button = driver.find_element_by_xpath(
            '//*[@id="details"]/form/div[4]/div/div/div/div[2]/div/div/input')
        year_button = driver.find_element_by_xpath(
            '//*[@id="details"]/form/div[4]/div/div/div/div[3]/div/div/input')
        notes_box = driver.find_element_by_xpath('//*[@id="details"]/form/div[5]/div[1]/div/textarea')
        month_button.click()
        month_button.send_keys(month)
        month_button.send_keys(Keys.ENTER)
        sleep(0.2)
        day_button.click()
        day_button.send_keys(day)
        day_button.send_keys(Keys.ENTER)
        sleep(0.2)
        year_button.click()
        year_button.send_keys(year)
        year_button.send_keys(Keys.ENTER)
        sleep(0.2)
        notes_box.send_keys(Keys.CONTROL + 'a' + Keys.BACKSPACE)
        notes_box.send_keys("Information from " + wiki_link)
        driver.find_element_by_xpath('//*[@id="details"]/form/div[5]/div[2]/button[1]').click()  # Submit button

    def update_episode(ep_num, update_info):
        month = update_info[0]
        day = update_info[1]
        year = update_info[2]
        driver.get(link(ep_num))
        driver.find_element_by_xpath(
            '//*[@id="content"]/div/div[2]/div/div/div[1]/div[4]/div/div[1]/div/a[2]').click()
        sleep(1)
        edit_page(day, month, year)

    update_logs = []
    for episode in update_list:
        print('**** Updating EP {}/{} ****'.format(episode[0],len(update_list)))
        try:
            update_episode(episode[0],episode[1])
            update_logs.append(episode[0])
        except Exception:
            pass
    return update_logs


def update_list(log,title):
    logstr = [str(ep_num)+'\n' for ep_num in log]
    with open('{}_logs.txt'.format(title.replace(' ','_')),'w') as logfile:
        logfile.writelines(logstr)


def open_log(title):
    try:
        with open('{}_logs.txt'.format(title.replace(' ','_')),'r') as logfile:
            updated = [ep.replace('\n', '') for ep in logfile.readlines()]
    except Exception:
        updated = []
    return updated