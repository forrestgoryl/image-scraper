<!-- Title -->
# image-scraper

<!-- Introduction -->
### A framework for automating the downloading of images from search engines and checking those downloads for duplicates, written in python. This program was designed with fetching images for machine learning in mind.

### **image-scraper** uses the selenium library to search for your keywords, enlarge each image on the search page, and then uses the requests library to download the image.

<!-- Video -->
[Video walkthrough](https://youtu.be/towKf-hvXiE)

<!-- Installation Instructions -->
**image-scraper** is executed in the command line. To use this application, a basic understanding of your command terminal of choice is required. The installation instructions are as follows:

1. Clone into this repository or select to download the zip file from the option under the green 'Code' icon on this webpage. If downloading the zip file, you will then need to extract the file contents to a suitable location.

2. Create a virtual environment with the command `virtualenv myenv` in the command line. I suggest you naming your environment something meaningful, such as `image-scraper-py3.9env`, simply replace `myenv` in the demo code with your desired environment name.

3. Activate your environment with the command `source myenv/Scripts/activate`.

4. Download necessary depencencies with the command `pip install -r requirements.txt`.

5. Add a new path that directs to the parent folder to your system's environment variables. The path you will add will be an absolute path, such as this: `C:\folder\folder\folder\image-scraper\`. You can name the path whatever you wish. This will allow geckodriver (a necessary part of the selenium module) to save logs into your project's folder. If you need assisstance doing this, there are many guides online and I'd encourage you to search for how to configure environment variables on your PC.

6. Try searching for a search term with `https://www.bing.com/images/search?q=`. Put this URL into any browser's searchbox and append a keyword of your choosing: `https://www.bing.com/images/search?q=dog`. Press enter. If the url returns appropriate results, then the program will function as intended. If this does not return suitable results, there could be a couple of reasons why it does not:
        - bing.com has different search URL expectations for your country
        - bing.com has changed what will work for a copy-and-paste search URL
Regardless, you will need to experiment with a different search URL. **image-scraper** expects to be able to append a keyword onto the end of a search URL, like in the above example. Try searching for a keyword the traditional way, such as going to your favorite search engine's homepage and then image searching. Look at the URL that results from your search, and try taking away different parts of it until you're left with a simple search URL with the keyword that you searched for on the very end. Copy that, put that into the browser searchbox and see if it returns the same result. If it does, you can use that new search URL (minus your keyword) in **image-scraper**. Open up `scrape_web.py` to modify what search URL the program uses.

Ok you're all set to begin scraping images!

<!-- Usage Instructions -->
### Usage Instructions:

- Place all keywords that you want to find images for inside of one of two keyword files: `keywords/positive.txt` or `keywords/negative.txt`. This choice is only relevant if you plan to use the scraped images for machine learning. If you want your network to produce a positive result upon seeing one keyword, put that keyword in the `positive.txt` file and vice versa for `negative.txt`.

- Run the program! Use either `python scrape_web.py` to scrape, or alternatively use `python scrape_web.py --see_browser` to show what the program is doing as it scrapes. **image-scraper** runs faster without `--see_browser` but this command can be useful if you need to see what's happening with selenium, or if you're just curious.

- After your search, run `python image_heap/check_duplicates.py` to check for duplicate downloads. This cleaning of data will take much longer than the actual search and so, if you are needing to clean over a thousand images, I suggest this be run overnight. It can be stopped using 'CRTL-c' and restarted by reexecuting `python image_heap/check_duplicates.py`. If reexecuting, consider using the additional argument `--reuse_log` to reuse the latest log in the folder, so as to keep all log data from the same clean operation within the same log file. Just incase you are confused about how to use `--reuse_log`, simply append the argument to the command line execution of check_duplicates ~ `python image_heap/check_duplicates.py --reuse_log`.
