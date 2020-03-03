# episodes() retrieves information of the series from ja.wikipedia.org and parses the necessary information into a
# list form to be updated on MDL
import requests
import bs4
from . import library


def episodes(title,season='all'):  # Generates a list with the episode numbers and its air dates
    native_title, root, wiki_link = library.links(title)
    page_src = requests.get(wiki_link)
    soup = bs4.BeautifulSoup(page_src.text, 'lxml')
    episode = dict()

    # Checks if series ends on the same year
    start_info = soup.find('th', text='放送期間').next_sibling.text.replace('\n', '').split(' - ')[0]
    end_info   = soup.find('th', text='放送期間').next_sibling.text.replace('\n', '').split(' - ')[-1]
    # Force airing shows to return single = False
    start_year = start_info.split('年')[0]
    end_year   = end_info.split('年')[0]
    if '年' not in end_info or end_year == start_year :  # Checks if series ends on the same year
        single = True # Will also trigger for multi-season shows. Declare season number as argument
        year_list = [table for table in soup.find_all(attrs={'class': 'wikitable'}) for entry in table.tbody.tr.contents
                     if '放送日' and '放送内容' in entry]
        if season != 'all':
            year_list = [year_list[int(season)-1]] # Selects the specific season (table number)
        else:
            pass
    else:
        single = False
        year_list = [table for table in soup.find_all(attrs={'class': 'NavFrame'}) if '年' in table.div.text]

    def extract_date_month(entry):
        entry = entry.split('年')[-1]
        month = entry.split('月')[0]
        date = entry.split('月')[1].split('日')[0]
        return date, month

    def extract_year(entry):  # Only single = False will trigger the use of entry
        if single:
            year = start_year
        else:
            year = entry.div.text[:4]  # Extracts the year
        return year

    def extract_eps(entry):
        if single:
            table = entry.find_all('tr')[1:]  # Removes first entry which is the header
        else:
            table = entry.find(attrs={'class': 'wikitable'}).find_all('tr')[1:]
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
            airdate = '{}-{}-{}'.format(year, month, date)
            episode[ep_num] = airdate
    else:
        pass

    # Converts dictionary information into a list
    ep_list = []
    ep_max = max(int(key) for key, value in episode.items() if key.isdigit()) + 1
    for i in range(1,ep_max):
        ep_list.append([str(i), entry(i)])
    return ep_list, root, wiki_link


def update(username, password, update_list, root, wiki_link):
    finished_list = []
    attempt = 0
    logged_in = False

    with requests.Session() as s:
        res = library.login(s, username, password)  # Logs in with payload as information
        while not logged_in and attempt < 4:
            username, password, logged_in, token = library.login_fail(res)
            attempt += 1
            res = library.login(s, username, password)

        if not logged_in and attempt == 3:
            print('Please try again later')
            exit()
        else:
            print('Successfully logged in')

        for ep, date in update_list:
            ep_page = s.get(root + ep)
            soup = bs4.BeautifulSoup(ep_page.text, 'lxml')
            ep_id = soup.find(attrs={'property': 'mdl:rid'})['content']
            try:
                update_res = s.post(library.update_link(ep_id, token), data=library.update_payload(wiki_link, date))
                if update_res.status_code == 200:  # For successful updates
                    finished_list.append(ep)
            except Exception:
                pass
    return finished_list