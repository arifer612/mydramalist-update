import mdl
import series
import log

username = input('USERNAME: >>>')
password = input('PASSWORD: >>>')
title = input('Series Title: >>>')
ask_season = input('Any specific season to consider? (y/n)') == 'y'
dir = "C:\\Users\\arife\\PycharmProjects\\HinaAi_DL"  # Temporary assert

if ask_season:
    while ask_season:
        season = input('Season number:')
        ask_season = input('Update season {}? (y/n)'.format(season)) != 'y'
else:
    season = 'all'
series_name = '{} {}'.format(title, season) if season != 'all' else title

updated = log.retrieve(series_name, dir)
ep_list, root, wiki_link = series.episodes(series_name)
update_list = [ep for ep in ep_list if ep[0] not in updated]
finished_list = mdl.episode_update(username, password, update_list, root, wiki_link)
done_list = updated + finished_list
done_list.sort(key=int)  # sorts numerically
log.save(done_list, series_name, dir)
print('Finished with the entry')
