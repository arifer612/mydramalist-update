import mdl_update

## Begin script
usr, pw = mdl_update.user_info()
print('What show do you wish to update?')
title = input('>>>')
root = mdl_update.search_for_title(title)
wiki_link = mdl_update.wiki(title)
episodes = mdl_update.ep_list(title)
updatebot = mdl_update.webdriver.Chrome()
mdl_update.login(updatebot, usr, pw)
log = mdl_update.seriesupdate(updatebot, root, episodes, wiki_link)
mdl_update.update_list(log, title)