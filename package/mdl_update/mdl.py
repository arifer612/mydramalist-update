# mdl.py contains the functions to be operated on the site
# The end-user will (ideally) only be using the function login() and seriesupdate()
# login() logs the user into MDL, returns nothing
# seriesupdate() edits the MDL series entry with the episodes' air-date and returns a list of successful edits
from Lib.library import user_info,


def login(driver, username='', password=''): # Logs into MDL
    if not username or not password:  # Check if non-empty
        username, password = library.user_info()

    logged_in = False
    attempts = 0
    while not logged_in and attempts < 3:
        library.login_page(driver, username, password)
        library.sleep(1)
        username, password, logged_in = library.login_fail(driver)
        attempts += 1
    if not logged_in and attempts==3:
        print("Please get the right account and password and try again later.")
        driver.quit()
        exit()


def seriesupdate(driver, root, update_list, wiki_link=''):
    # root : MyDramaList link to the series
    # update_list: may be shortened to remove already updated episodes by keeping comparing against a log file
    def link(i):
        return '{}{}'.format(root, i)

    def edit_page(day, month, year):
        library.sleep(1)
        month_button = driver.find_element_by_xpath(
            '//*[@id="details"]/form/div[4]/div/div/div/div[1]/div/div/input')
        day_button = driver.find_element_by_xpath(
            '//*[@id="details"]/form/div[4]/div/div/div/div[2]/div/div/input')
        year_button = driver.find_element_by_xpath(
            '//*[@id="details"]/form/div[4]/div/div/div/div[3]/div/div/input')
        notes_box = driver.find_element_by_xpath('//*[@id="details"]/form/div[5]/div[1]/div/textarea')
        month_button.click()
        month_button.send_keys(month)
        month_button.send_keys(library.Keys.ENTER)
        library.sleep(0.2)
        day_button.click()
        day_button.send_keys(day)
        day_button.send_keys(library.Keys.ENTER)
        library.sleep(0.2)
        year_button.click()
        year_button.send_keys(year)
        year_button.send_keys(library.Keys.ENTER)
        library.sleep(0.2)
        notes_box.send_keys(library.Keys.CONTROL + 'a' + library.Keys.BACKSPACE)
        notes_box.send_keys("Information from {}".format(wiki_link))
        library.sleep(0.2)
        driver.find_element_by_xpath('//*[@id="details"]/form/div[5]/div[2]/button[1]').click()  # Submit button

    def update_episode(ep_num, update_info):
        month = update_info[0]
        day = update_info[1]
        year = update_info[2]
        driver.get(link(ep_num))
        driver.find_element_by_xpath(
            '//*[@id="content"]/div/div[2]/div/div/div[1]/div[4]/div/div[1]/div/a[2]').click()
        library.sleep(1)
        edit_page(day, month, year)

    update_logs = [] # Creates empty list to store episodes that have been successfully updated
    for episode in update_list:
        print('**** Updating EP {}/{} ****'.format(episode[0],len(update_list)))
        try:
            update_episode(episode[0],episode[1])
            update_logs.append(episode[0])
        except Exception:
            pass
    return update_logs