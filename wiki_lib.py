from googlesearch import search


def link(title):
    query = title + ' wikipedia jp'
    wiki_link = [link for link in search(query, lang='jp', start=0, stop=1, pause=0.1)][0]
    return wiki_link


def extract_date_month(entry):  # Function to extract the dates and months
    entry = entry.split('年')[-1]
    month = entry.split('月')[0]
    date = entry.split('月')[1].split('日')[0]
    return date, month


def extract_airdate():
