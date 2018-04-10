This is Sofascore livescore scraper.
Requirements:
- Python 2.7 ( https://www.python.org/ftp/python/2.7.14/python-2.7.14.msi *** You need to add the python27 to the environment variables), and the following python modules:
  - requests
  - json
  - os
  - sys
  - traceback
  - time
  - datetime from datetime
  *** From the above, you need to install additionaly requests and BeautifulSoup by following the below instuctions:
  1. Open cmd from the Start menu
  2. Go to the Python27 folder, located at C:\
  3. Navigate to Python27\Scripts folder ( something like cd Scripts ), when you're in C:\Python27
  4. Install requests, using pip with the following command: "pip install requests"
  5. Install bs4, using pip: "pip install bs4"
  If the above steps are completed without a problem, you're ready to run the scraper files.
  
1. How it's made: It uses a main Sofascore class, where the methods for all sports should be written. The parameters needed for initializing new instance are sleeptime, sport and period.
1.1. When the Sofascore is instanted, the start() method must be called to make it run.
     What will happen after that is, a request to the sport URL, collecting information into a dict and them dumping the dict to 
     .json in a directory.
     Currently there are 3 periods setted for soccer: Live, Prematch and Finished, where the difference between them is that in Finished
     there are no odds, and there are some specific properties in the Live version.
     !Important note is that the Sofascore's API gives all the needed information for scraping, i.e. there is no need of Logged in user.


RUNNING the scrapers:
1. Navigate with the cmd to the folder within are located the scraper files (scrape_soccer_finished.py and the others).
2. Run the wanted scraper with the following command: "python scrape_name.py".
3. That's it. Check the scraper_debug directory, and there are the latest .json files with scraped data.
