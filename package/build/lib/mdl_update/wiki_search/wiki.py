from googlesearch import search
import bs4
import requests


def wiki(title): # Searches for wikipedia link. Search term has to be accurate
    query = title + ' wikipedia jp'
    wiki_link = [link for link in search(query, lang='jp', start=0, stop=1, pause=0.1)][0]
    return wiki_link


def episodes(title): # Generates a list with the episode numbers and its air dates
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