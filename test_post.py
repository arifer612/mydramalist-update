# Submits changes without the need of a browser (so much easier this way)

import requests
import bs4


def login_payload(username,password):
    return {
    'username': username,
    'password': password
}


def update_payload(wiki_link,date):
    return {
    'category':'details',
    'notes':'Information from {}'.format(wiki_link),
    'release_date':date
}


def update_link(id,token):
    return 'https://mydramalist.com/v1/edit/episodes/{}/details?lang=undefined&token={}'.format(id,token)


def episode_update(update_list,username,password,wiki_link,date):
    finished_list = []
    with requests.Session() as s:
        res = s.post('https://mydramalist.com/signin', data=login_payload(username,password)) # Logs in with payload as information
        token = res.request.headers['Cookie'].split(';')[1].split('=')[1]
        for link in update_list:
            ep_page = s.get(link)
            soup = bs4.BeautifulSoup(ep_page.text,'lxml')
            ep_id = soup.find(attrs={'property':'mdl:rid'})['content']
            try:
                update_res = s.post(update_link(ep_id,token), data=update_payload(wiki_link,date))
                if update_res.status_code == 200: # For successful updates
                    print('save to log')
            except Exception:
                pass