# episodes() retrieves information of the series from ja.wikipedia.org and parses the necessary information into a
# list form to be updated on MDL
import requests
import bs4
from . import library
import datetime
import re


def episodes(title, season=None):  # Generates a list with the episode numbers and its air dates
    native_title, root, wiki_link = library.links(title + ' ' + season if season and season != '1' else title)
    page_src = requests.get(wiki_link)
    soup = bs4.BeautifulSoup(page_src.text, 'lxml')
    episode = dict()

    if season:
        info = soup.find_all(attrs={'style': 'text-align:center;background-color: #FDEBD0;'})[
            int(season) - 1]  # Find orange box
        info = info.parent.next_sibling.td  # Gets the 放送期間 information
        start_info = info.text.replace('\n', '').partition(' - ')[0]
        end_info = info.text.replace('\n', '').partition(' - ')[-1]
    else:
        start_info = soup.find('th', text='放送期間').next_sibling.text.replace('\n', '').partition(' - ')[0]
        end_info = soup.find('th', text='放送期間').next_sibling.text.replace('\n', '').partition(' - ')[-1]

    start_year = start_info.split('年')[0]
    end_year   = end_info.split('年')[0] if end_info != ' - ' else None

    if end_year:  # Completed
        if '年' not in end_info or start_year == end_year:  # Check if series started airing this year
            single = True  # Will also trigger for multi-season shows. Declare season number as argument
        else:
            single = False
    elif start_year == str(datetime.date.today().year):
        single = True
    else:
        single = False

    def table_list(single):
        if single:
            year_list = [table for table in soup.find_all(attrs={'class': 'wikitable'}) for entry in
                         table.tbody.tr.contents
                         if '放送日' and '放送内容' in entry]
            if not year_list:
                year_list = [table for table in soup.find_all(attrs={'class': 'wikitable'}) for entry in
                         table.tbody.tr.contents
                         if '放送日' and '配信日' in entry] # Added for shows with stream dates instead
            else:
                pass
            if season:
                year_list = [year_list[int(season) - 1]]  # Selects the specific season (table number)
            else:
                pass
        else:
            year_list = [table for table in soup.find_all(attrs={'class': 'NavFrame'}) if '年' in table.div.text]
        return year_list

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

    for year_entry in table_list(single):
        year = extract_year(year_entry)
        for ep in extract_eps(year_entry):
            ep_num, date, month = extract_ep_and_date(ep)
            airdate = '{}-{}-{}'.format(year, month, date)
            episode[ep_num] = airdate
    else:
        pass

        # Converts dictionary information into a list
    ep_list = []
    eps = [key for key in episode.keys() if re.sub('\D','',key)] # Extracts only numbered episodees
    for ep in eps:
        ep_list.append([re.sub('\D','',ep), episode[ep]]) # [ep num, ep airdate]
    return ep_list, root, wiki_link


def update(username, password, update_list, root, wiki_link, additional_info=None):
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
        try:
            ep_id = soup.find(attrs={'property': 'mdl:rid'})['content']
            update_res = s.post(library.update_link(ep_id, token),
                                data=library.update_payload(wiki_link, date, additional_info))
            if update_res.status_code == 200:  # For successful updates
                finished_list.append(ep)
        except Exception:
            pass
    return finished_list
