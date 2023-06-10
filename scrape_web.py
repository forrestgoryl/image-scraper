from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from os import listdir, mkdir, remove, path
import requests, sys, time



def yield_keywords(file):
    
    # Open file
    with open(file, 'r') as keywords:

        # read lines in file
        for line in keywords.readlines():

            # yield line without spaces or newline characters
            yield line.replace(' ', '+').replace("\n", '')


def ready_webpage(wait, driver, desired_img_amount):

    # Scroll webpage to load more images
    for i in range(3):
        
        # Scroll to bottom of page
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

        # Wait a few seconds
        time.sleep(3)

    return driver


def yield_suitable_imgs(img_tags):

    # Iterate through img_tags
    for e in img_tags:

        # If pixel count is >= 4500
        if e.size['height'] * e.size['width'] >= 4500:

            yield e


def return_save_folder(kw, parent_save_folder):

    # Returns positive save_folder or negative save_folder
    if kw in positive_keywords:
        return parent_save_folder + 'positive/'
    else:
        return parent_save_folder + 'negative/'


def locate_largest_img_element(img_tags):

    # Define trackers
    largest_pixel_count = 0
    largest_element = None

    # Iterate through each element, keeping track of largest element
    for element in img_tags:
        try:
            size = element.size
        except NoSuchElementException:
            size = None
        if size != None:
            pixel_count = size['height'] * size['width']
            if pixel_count > largest_pixel_count:
                largest_pixel_count = pixel_count
                largest_element = element

    return largest_element


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

    # Append kw to used kw log
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


    
def log(message, log_file):
    
    # Open log file
    with open(log_file, 'a') as f:
        
        # Write message + newline
        f.write(message + '\n')


def get_log_file():

    if '--reuse_log' not in sys.argv:
        # Define variables
        name, i = None, 0

        # Continue to rename 'name' until no file is found in 'logs/' with same name
        while name == None or path.exists(name):
            i += 1
            name = 'logs/scrape_log_{}.txt'.format(i)
        
        return name
    
    # if --reuse_log was specified as an argument during cmd line execution
    else:
        files_amt = len(listdir('logs/'))
        return 'logs/scrape_log_{}.txt'.format(files_amt)



if __name__ == '__main__':

    print('''\nProgram expects

    *All positive-outcome keywords be in keywords/positive_kw.txt

    *All negative-outcome keywords be in keywords/negative_kw.txt

    *Scrape is done in 'headless' mode by default,
    if browser visibility is desired add the argument '--see_browser'
    to command line execution of program

    *The argument '--reuse_log' can also be stated in command line execution
    to append results to most recent log 
    (useful for starting a previously-stopped scrape again, to share same log)
    \n''')
    
    positive_keywords = list(yield_keywords('keywords/positive_kw.txt'))
    negative_keywords = list(yield_keywords('keywords/negative_kw.txt'))

    log_file = get_log_file()

    # Search engine urls are meant to allow kw to be appended to the end of them
    # and be a useable search url afterward. Adding new search engine urls might take
    # some experimenting
    search_engine_urls = ['https://www.bing.com/images/search?q=']

    parent_save_folder = 'image_heap/unchecked/'

    # Disable browser caching in driver
    options = Options()
    options.set_preference('browser.cache.disk.enable', False)
    options.set_preference('browser.cache.memory.enable', False)
    options.set_preference('browser.cache.offline.enable', False)
    options.set_preference('network.http.use-cache', False)

    # Enable headless mode
    if '--see_browser' not in sys.argv:
        options.add_argument('-headless')

    # Create a new instance of the Firefox browser driver
    driver = webdriver.Firefox(options=options)    

    # Define basic wait amount
    wait = WebDriverWait(driver, 10)

    # for use in 'wait' functions
    img_locator = (By.TAG_NAME, 'img')

    # Run scraper inside of try... except... finally so driver 
    # can close properly even with error raised
    try:
        for kw in positive_keywords + negative_keywords:
            message = 'Searching for ' + kw + '\n'
            log(message, log_file)
            print(message)
            
            downloads = {
                'success': 0,
                'failure': 0
            }

            save_folder = return_save_folder(kw, parent_save_folder)

            if not path.exists(save_folder):
                mkdir(save_folder)

            # Open browser, search, then ready webpage
            for url in search_engine_urls:
                message = 'Opening ' + url + kw + '\n'
                log(message, log_file)
                print(message)
                driver.get(url + kw)
                driver = ready_webpage(wait, driver, 200)

                # Isolate all <img> tags
                img_tags = driver.find_elements(*img_locator)

                # Filter <img> tags by size, keeping the suitable ones
                suitable_imgs = yield_suitable_imgs(img_tags)

                # Iterate through each <img> WebElement
                for element in suitable_imgs:
                    
                    # Try to click on the element
                    clicked = False
                    try:
                        element.click()
                        clicked = True
                    except Exception as e:
                        message = 'Experienced exception when clicking on element'
                        log(message, log_file)
                        # log(str(e.args), log_file)
                        print(message)
                    if clicked:
                        

                        # Check if there are two or more tabs open
                        if len(driver.window_handles) > 1:\

                            # Close all tabs except the first one
                            for handle in driver.window_handles[1:]:
                                driver.switch_to.window(handle)
                                driver.close()

                            # Switch back to the first tab
                            driver.switch_to.window(driver.window_handles[0])

                        # Set download_success to false
                        download_success = False

                        # Switch driver focus to <iframe>
                        iframe = driver.find_element(By.TAG_NAME, 'iframe')
                        driver.switch_to.frame(iframe)

                        # Locate largest <img> WebElement
                        img_tags = wait.until(EC.presence_of_all_elements_located(img_locator))
                        if img_tags != None:
                            largest_img_element = locate_largest_img_element(img_tags)
                            if largest_img_element != None:
                                try:
                                    # Request image data
                                    src = largest_img_element.get_attribute('src')
                                    response = requests.get(src)
                                    
                                    # Define save path
                                    filename = f'{len(listdir(save_folder)) + 1}.jpg'
                                    filepath = save_folder + filename

                                    # save file
                                    with open(filepath, 'wb') as file:
                                        file.write(response.content)
                                    
                                    # log result
                                    downloads['success'] += 1
                                    message = 'Downloaded ' + filename
                                    log(message, log_file)
                                    print(message)
                                    
                                except Exception as e:
                                    message = 'Experienced exception when requesting or writing image data'
                                    log(message, log_file)
                                    # log(str(e.args), log_file)
                                    print(message)
                                    print(str(e.args))
                                    downloads['failure'] += 1
                        
                        # Switch driver focus back
                        driver.switch_to.default_content()
                        
                        # Navigate back to starting page
                        driver.back()

            # Log and print results
            messages = [
                '\nResults for ' + kw,
                f'Successes: {downloads["success"]}, failures: {downloads["failure"]}\n'
            ]
            for mes in messages:
                log(mes, log_file)
                print(mes)

            # Erases kw from kw_file and appends to used_kw_log
            cycle_kw(kw, positive_keywords)

    except Exception as e:

        # Reassure user that the program is stopping
        print('\nProgram is stopping... Do not hit crtl-c\n')

        # Erase last result from used kw log
        used_kw_log = 'keywords/used_kw_log.txt'
        with open(used_kw_log, 'r') as f:
            contents = [line.replace('\n', '') for line in f.readlines()]
        contents.pop(-1)
        with open(used_kw_log, 'w') as f:
            f.write('\n'.join(contents))
        
        # Print error
        print(str(e) + '\n')

        # Print results obtained up to the exception
        messages = [
            '\nResults for ' + kw,
            f'Successes: {downloads["success"]}, failures: {downloads["failure"]}\n'
        ]
        for mes in messages:
            log(mes, log_file)
            print(mes)
        
    finally:
        driver.close()