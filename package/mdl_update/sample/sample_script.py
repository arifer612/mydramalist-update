import mdl_update as m

username = input('USERNAME: >>>')
password = input('PASSWORD: >>>')
title = input('Series Title: >>>')
ask_season = input('Any specific season to consider? (y/n)') == 'y'

if ask_season:
    while ask_season:
        season = input('Season number:')
        ask_season = input('Update season {}? (y/n)'.format(season)) != 'y'
else:
    season = 'all'
series_name = '{} {}'.format(title, season) if season != 'all' else title

updated = m.log.retrieve(series_name, dir)
ep_list, root, wiki_link = m.series.episodes(series_name)
update_list = [ep for ep in ep_list if ep[0] not in updated]
finished_list = m.series.update(username, password, update_list, root, wiki_link)
done_list = updated + finished_list
done_list.sort(key=int)  # sorts numerically
m.log.save(done_list, series_name, dir)
print('Finished with the entry')
