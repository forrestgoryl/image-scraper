from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from helpers import log
import helpers, os, sys, time


# Search engine URLs are meant to allow keywords to be appended to the end of them
# and be a useable search URL afterward. In other words, search engine urls should end
# with 'q='. Do not worry about keyphrases and spaces being appended to these urls and
# not working; yield_keywords() automatically solves this problem.
SEARCH_ENGINE_URLS = [
    'https://www.bing.com/images/search?q=',
]


# Defines the minimum size of image the program will click on. Adjusting is useful
# if program gets hung up on small icons that are links to other search pages and not
# actually image links.
SUITABLE_IMAGE_SIZE = 130*130


def ready_webpage(wait, driver, scroll_amount):

    # Scroll webpage to load more images
    for i in range(scroll_amount):

        # Scroll to bottom of page
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

        # Wait for 3 seconds
        time.sleep(3)

    return driver


def yield_suitable_imgs(imgs):

    # Iterate through imgs
    for element in imgs:

        # If img is >= SUITABLE_IMAGE_SIZE
        if element.size['height'] * element.size['width'] >= SUITABLE_IMAGE_SIZE:

            yield element


def locate_largest_img(imgs):

    # Define trackers
    largest_pixel_count = 0
    largest_element = None

    # Iterate through each element, keeping track of largest element
    for element in imgs:
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


if __name__ == '__main__':

    print('''
    Program expects

    *All positive-outcome keywords be in keywords/positive_kw.txt

    *All negative-outcome keywords be in keywords/negative_kw.txt

    Scrape is done in 'headless' mode by default,
    if browser visibility is desired add the argument '--see_browser'
    to command line execution of program

    The argument '--reuse_log' can also be stated in command line execution
    to append results to most recent log 
    (useful for starting a previously-stopped scrape again, to share same log)
    \n''')
    
    # Grab keywords lists
    positive_keywords = list(helpers.yield_keywords('keywords/positive_kw.txt'))
    negative_keywords = list(helpers.yield_keywords('keywords/negative_kw.txt'))

    # Define where to log
    log_file = helpers.get_log_file(sys.argv)

    # Setup webdriver Options (disable caching, use private browsing, etc.)
    options = helpers.setup_options(sys.argv)

    # For use in 'wait' and 'find_elements' functions 
    # (defined here so as to not redefine in for loops)
    img_locator = (By.TAG_NAME, 'img')

    for kw in positive_keywords + negative_keywords:

        try:

            # Create new instance of Firefox
            driver = webdriver.Firefox(options=options)

            # Define wait amount (in seconds)
            wait = WebDriverWait(driver, 10)

            message = 'Searching for ' + kw + '\n'
            log(message, log_file)
            print(message)

            # Search for kw in each search engine
            for url in SEARCH_ENGINE_URLS:

                message = 'Opening ' + url + kw + '\n'
                log(message, log_file)
                print(message)

                # Open browser
                driver.get(url + kw)

                # Scroll to load more images
                driver = ready_webpage(wait, driver, scroll_amount=3)

                # Find all image elements
                img_elements = driver.find_elements(*img_locator)

                # Reload webpage if images aren't located
                while len(img_elements) < 15:
                    
                    # Wait between get requests so as to not annoy search engine server
                    time.sleep(10)

                    driver.get(url + kw)
                    img_elements = driver.find_elements(*img_lcator)

                # Filter image elements by size
                suitable_imgs = yield_suitable_imgs(img_elements)

                # Define variable for logging performance
                downloads = {
                    'success': 0,
                    'failure': 0
                }
                
                # Iterate through each suitable image
                for element in suitable_imgs:

                    # Scroll to the element
                    driver.execute_script("arguments[0].scrollIntoView({block: 'start', inline: 'start', behavior: 'smooth'});", element)

                    # Wait until element is clickable
                    wait.until(EC.element_to_be_clickable(element))

                    # Click on element
                    try:
                        element.click()
                        clicked = True
                    except Exception as e:
                        clicked = False
                        message = 'Experienced exception when clicking on element'
                        log(message, log_file)
                        print(message)
                        # log(f'type of error: {type(e)}\n{str(e)}', log_file)  # Uncomment to log full exception
                        # print(f'type of error: {type(e)}\n{str(e)}')          # Uncomment to print full exception

                    if clicked:

                        # Wait for webdriver to be fully ready
                        time.sleep(0.5)

                        # Handle new tabs
                        driver = helpers.handle_new_tab(driver)

                        # Wait for webdriver to be fully ready
                        time.sleep(0.5)

                        # Switch driver focus to iframe if exists
                        iframe = driver.find_element(By.TAG_NAME, 'iframe')
                        driver.switch_to.frame(iframe)

                        # Wait for webdriver to be fully ready
                        time.sleep(0.5)

                        # Locate largest image in iframe
                        try:
                            iframe_img_elements = wait.until(EC.presence_of_all_elements_located(img_locator))
                        except TimeoutException:
                            iframe_img_elements = None

                        if iframe_img_elements != None:

                            # Locate largest image
                            largest_img = locate_largest_img(iframe_img_elements)

                            if largest_img != None:

                                try:
                                    # Get src
                                    src = largest_img.get_attribute('src')

                                    # Create absolute path to save location
                                    filepath = helpers.return_filepath(kw, positive_keywords)

                                    # Save image
                                    helpers.save_img(src, filepath)

                                    # Log download success
                                    downloads['success'] += 1
                                    message = 'Downloaded ' + filepath
                                    log(message, log_file)
                                    print(message)

                                except Exception as e:

                                    # Log download failure
                                    downloads['failure'] += 1
                                    message = 'Experienced exception when saving image (during request of or writing of image)'
                                    log(message, log_file)
                                    print(message)
                                    
                                    # log(f'type of error: {type(e)}\n{str(e)}', log_file)  # Uncomment to log full exception
                                    # print(f'type of error: {type(e)}\n{str(e)}')          # Uncomment to print full exception

                        # Switch driver focus back
                        driver.switch_to.default_content()

                        # Navigate back to starting page
                        driver.back()

                # Erase keyword from appropriate keywords/*.txt file
                # and appends to keywords/used_kw_log.txt
                helpers.cycle_kw(kw, positive_keywords)

                # Wait for search engine server to not get mad at quantity of requests
                time.sleep(10)
            
            # Shut driver off (will start new one at beginning of loop if continuing)
            driver.close()


        except KeyboardInterrupt:

            # Assure user program is stopping
            print('\nProgram stopping\n')

            driver.close()
            sys.exit()

        except Exception as e:
            
            message =   f'''
                        Experienced exception while searching for {kw}
                        Exception was type {type(e)}
                        ''' + '\n' + str(e)
            log(message, log_file)
            print(message)

        finally:

            # Record results
            if 'downloads' in globals():
                messages = [
                    '\n Results for ' + kw,
                    'Successes: {}, failures: {}\n'.format(downloads['success'], downloads['failure'])
                ]
                for message in messages:
                    log(message, log_file)
                    print(message)