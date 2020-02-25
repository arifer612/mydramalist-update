# episodes() retrieves information of the series from ja.wikipedia.org and parses the necessary information into a
# list form to be updated on MDL
import requests
import bs4
import library


def episodes(title):  # Generates a list with the episode numbers and its air dates
    root, wiki_link = library.links(title)
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
        single = True
        year_list = [table for table in soup.find_all(attrs={'class': 'wikitable'}) for entry in table.tbody.tr.contents
                     if '放送日' and '放送内容' in entry]
    else:
        single = False
        year_list = [table for table in soup.find_all(attrs={'class': 'NavFrame'}) if '年' in table.div.text]

    try:
        seasons = [season.text for season in
                   soup.find_all(attrs={'style': 'text-align:center;background-color: #FDEBD0;'}) if '年' not in
                   season.text]
    except Exception:
        pass

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

    # Converts dictionary information into a list
    ep_list = []
    ep_max = max(int(key) for key, value in episode.items() if key.isdigit()) + 1
    for i in range(1,ep_max):
        ep_list.append([i, entry(i)])
    return ep_list, root, wiki_link, episode