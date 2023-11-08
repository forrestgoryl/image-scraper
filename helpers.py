from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import requests, os

PARENT_OF_SAVE_FOLDER = 'image_heap/unchecked/'


def cycle_kw(kw, positive_keywords):

    # Define variables
    parent = 'keywords/'
    used_kw_log = parent + 'used_kw_log.txt'

    # Get kw file
    if kw in positive_keywords:
        kw_file = parent + 'positive_kw.txt'
    else:
        kw_file = parent + 'negative_kw.txt'

    # Replace '+' in kw with space
    kw = kw.replace('+', ' ')

    # Append kw to used_kw_log
    with open(used_kw_log, 'a') as f:
        f.write(kw + '\n')
    
    # Copy contents of kw file
    with open(kw_file, 'r') as f:
        contents = [line.replace('\n', '') for line in f.readlines()]
    
    # Remove kw from contents
    contents.remove(kw)

    # Write new contents to kw file
    with open(kw_file, 'w') as f:
        f.write('\n'.join(contents))


def get_log_file(args):

    if '--reuse_log' not in args:
        # Define variables
        name, i = None, 0

        # Continue to rename 'name' until no file is found in 'logs/' with same name
        while name == None or os.path.exists(name):
            i += 1
            name = 'logs/scrape_log_{}.txt'.format(i)
        
        return name
    
    # if --reuse_log was specified as an argument during cmd line execution
    else:
        files_amt = len(os.listdir('logs/'))
        return 'logs/scrape_log_{}.txt'.format(files_amt)


def handle_new_tab(driver):

    # Check if there are two or more tabs open
    if len(driver.window_handles) > 1:

        # Close all tabs except the first one
        for handle in driver.window_handles[1:]:
            driver.switch_to.window(handle)
            driver.close()

        # Switch back to the first tab
        driver.switch_to.window(driver.window_handles[0])

    # Hand back driver
    return driver



def log(message, log_file):
    
    # Open log file
    with open(log_file, 'a') as f:
        
        # Write message + newline
        f.write(message + '\n')


def return_filepath(kw, positive_keywords):

    # Returns positive save_folder or negative save_folder
    if kw in positive_keywords:
        save_folder = PARENT_OF_SAVE_FOLDER + 'positive/'
    else:
        save_folder = PARENT_OF_SAVE_FOLDER + 'negative/'

    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    # Define filename
    filename = f'{len(os.listdir(save_folder)) + 1}.jpg'

    # Craft filepath
    filepath = save_folder + filename

    return filepath


def save_img(src, filepath):

    # Request image data
    response = requests.get(src)

    # save file
    with open(filepath, 'wb') as file:
        file.write(response.content)


def setup_options(args):

    # Define options
    options = Options()

    # Disable browser caching in driver and use private browsing
    options.set_preference('browser.cache.disk.enable', False)
    options.set_preference('browser.cache.memory.enable', False)
    options.set_preference('browser.cache.offline.enable', False)
    options.set_preference('network.http.use-cache', False)
    options.set_preference('browser.privatebrowsing.autostart', True)

    # Enable headless mode
    if '--see_browser' not in args:
        options.add_argument('-headless')

    return options


def yield_keywords(file):
    
    # Open file
    with open(file, 'r') as keywords:

        # read lines in file
        for line in keywords.readlines():

            # yield line without spaces or newline characters
            yield line.replace(' ', '+').replace("\n", '')