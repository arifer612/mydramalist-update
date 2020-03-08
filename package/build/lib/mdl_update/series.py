# episodes() retrieves information of the series from ja.wikipedia.org and parses the necessary information into a
# list form to be updated on MDL
import requests
import bs4
from . import library
import datetime
import re


def wiki(title, season=None, lang='jp', column_param=None):  # Generates a list with the episode numbers and its air dates
    # 'Forced' forces us to consider it as a single season entry. Works for single season shows that end in the next
    # year.
    if season == 'Forced':
        forced = 1
        season = None
    elif season == 'Unforced':
        forced = -1
        season = None
    else:
        forced = 0

    if lang == 'jp':
        terms = ['放送期間','年','月','日']
    elif lang =='ko':
        terms = ['방송 기간','년', '월', '일']

    native_title, root, wiki_link = library.links(title + ' ' + season if season and season != '1' else title, lang)

    # Scraping information from Wiki
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
        try:
            start_info = soup.find('th', text=terms[0]).next_sibling.text.replace('\n', '').partition(' - ')[0]
            end_info   = soup.find('th', text=terms[0]).next_sibling.text.replace('\n', '').partition(' - ')[-1]
        except Exception:
            start_info = '2013년 11월 3일' # Too lazy to generalise. Sloppy work here
            end_info = ' - ' # Here too

    start_year = start_info.split(terms[1])[0]
    end_year = end_info.split(terms[1])[0] if end_info != ' - ' else None

    if forced == 0:
        if end_year:  # Completed
            if terms[1] not in end_info or start_year == end_year:  # Check if series started airing this year
                single = True  # Will also trigger for multi-season shows. Declare season number as argument
            else:
                single = False
        elif start_year == str(datetime.date.today().year):
            single = True
        else:
            single = False
    elif forced == 1:
        single = True
    else:
        single = False

    def table_list(single):
        add_column = ['放送内容', '配信日', '各話', '企画内容', '授業内容', '企画']
        add_column = add_column + [column_param] if column_param else add_column
        if single:
            for column_entry in add_column:
                year_list = [table for table in soup.find_all(attrs={'class': 'wikitable'}) for entry in
                             table.tbody.tr.contents
                             if '放送日' and column_entry in entry]
                if year_list:
                    break
                else:
                    pass
            if season:
                year_list = [year_list[int(season) - 1]]  # Selects the specific season (table number)
            else:
                pass
        else:
            if lang == 'jp':
                year_list = [table for table in soup.find_all(attrs={'class': 'NavFrame'}) if '年' in table.div.text]
            elif lang == 'ko':
                year_list = [table for table in soup.find_all('h4')]
        return year_list

    def extract_date_month(entry):
        entry = entry.split(terms[1])[-1]
        month = entry.split(terms[2])[0]
        date = entry.split(terms[2])[1].split(terms[3])[0].replace(' ','')
        return date, month

    def extract_year(entry):  # Only single = False will trigger the use of entry
        if single:
            year = start_year
        else:
            if lang == 'jp':
                year = entry.div.text.replace(' ','')[:4]  # Extracts the year
            elif lang == 'ko':
                year = entry.find(class_ = 'mw-headline')['id'].replace(' ','')[:4]
        return year

    def extract_eps(entry):
        if single:
            table = entry.find_all('tr')[1:]  # Removes first entry which is the header
        else:
            if lang == 'jp':
                table = entry.find(attrs={'class': 'wikitable'}).find_all('tr')[1:]
            elif lang =='ko':
                try:
                    table = entry.next_sibling.next_sibling.find(attrs={'class': 'wikitable'}).find_all('tr')[2:]
                except Exception:
                    table = entry.next_sibling.next_sibling.find_all('tr')[2:]
        return table

    def extract_ep_and_date(entry):  # Entry here is the 'tr' class
        dateinfo = [info for info in entry.contents]  # Extracts the date
        ep_num = dateinfo[1].text.replace('\n', '')
        date, month = extract_date_month(dateinfo[3].text)
        return ep_num, date, month

    for year_entry in table_list(single):
        try:
            year = extract_year(year_entry)
            for ep in extract_eps(year_entry):
                try:
                    ep_num, date, month = extract_ep_and_date(ep)
                    airdate = '{}-{}-{}'.format(year, month, date)
                    episode[ep_num] = airdate
                except Exception:
                    pass  # Ignore episodes that fail to be found
        except Exception:
            pass

    wiki_dict = {re.sub('\D', '', ep): episode[ep] for ep in episode.keys() if
                 re.sub('\D', '', ep)}  # Only show numbered episodes
    return wiki_dict, root, wiki_link


def mdl(root):
    # Scraping information from MDL
    batch_link = root[:-1] + 's'
    res = requests.get(batch_link)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    mdl_ep = soup.find(class_='episodes clear m-t')
    episodes = mdl_ep.find_all(class_='episode')

    def get_info(episode):
        ep = episode.find(class_='title').a.text
        ep_num = ep.split('Episode ')[1]
        try:
            air = episode.find(class_='air-date').text
            date_info = datetime.datetime.strptime(air, '%b %d, %Y')
            air_date = datetime.datetime.strftime(date_info, '%Y-%m-%d').replace('-0', '-')
        except Exception:
            air_date = ''
        return ep_num, air_date

    mdl_list = {}
    for episode in episodes:
        ep_num, air_date = get_info(episode)
        if re.sub('\D', '', ep_num):
            mdl_list[re.sub('\D', '', ep_num)] = air_date
        else:
            pass

    return mdl_list


def update_list(title, season=None, lang='jp', column_param=None):
    # Wiki infomation
    wiki_dict, root, wiki_link = wiki(title, season, lang, column_param)

    # MDL information
    mdl_dict = mdl(root)

    # Create update_list
    update_list = {ep: wiki_dict[ep] for ep in wiki_dict if ep not in mdl_dict or mdl_dict[ep] != wiki_dict[ep]}
    return update_list, root, wiki_link


def update(username, password, update_list, root, wiki_link, additional_info=None):
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

    def adj(num,length):
        return str(num).rjust(length)

    for num, (ep, date) in enumerate(update_list.items(), start=1):
        ep_page = s.get(root + ep)
        soup = bs4.BeautifulSoup(ep_page.text, 'lxml')
        size = len(str(len(update_list)))
        try:
            ep_id = soup.find(attrs={'property': 'mdl:rid'})['content']
            update_res = s.post(library.update_link(ep_id, token),
                                data=library.update_payload(wiki_link, date, additional_info))
            if update_res.status_code == 200:  # For successful updates
                print('({}/{}) Successfully updated Episode {} with date {}'.format(adj(num, size),
                                                                                    len(update_list),
                                                                                    adj(ep,size),
                                                                                    date.ljust(10)
                                                                                    )
                      )

            else:
                print('({}/{}) >Failed< to update  Episode {} with date {}'.format(adj(num, size),
                                                                                    len(update_list),
                                                                                    adj(ep,size),
                                                                                    date.ljust(10)
                                                                                   )
                      )
        except Exception:
            print('({}/{}) Episode {} not found'.format(adj(num, size),
                                                        len(update_list),
                                                        adj(ep, size)
                                                        )
                  )