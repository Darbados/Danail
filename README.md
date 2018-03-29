This is Sofascore livescore scraper.
Requirements:
- Python 2.7, and the following python modules:
  - requests
  - json
  - os
  - sys
  - traceback
  - time
  - datetime from datetime
  
1. How it's made: It uses a main Sofascore class, where the methods for all sports should be written. The parameters needed for initializing new instance are sleeptime, sport and period.
1.1. When the Sofascore is instanted, the start() method must be called to make it run.
     What will happen after that is, a request to the sport URL, collecting information into a dict and them dumping the dict to 
     .json in a directory.
     Currently there are 3 periods setted for soccer: Live, Prematch and Finished, where the difference between them is that in Finished
     there are no odds, and there are some specific properties in the Live version.
     !Important note is that the Sofascore's API gives all the needed information for scraping, i.e. there is no need of Logged in user.
