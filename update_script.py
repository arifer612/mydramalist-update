import update

## Begin script
usr, pw = update.user_info()
print('What show do you wish to update?')
title = input('>>>')
root = update.search_for_title(title)
wiki_link = update.wiki(title)
episodes = update.ep_list(title)
updatebot = update.webdriver.Chrome()
update.login(updatebot,usr,pw)
log = update(updatebot,root,episodes,wiki_link)
update.updated_list(log)