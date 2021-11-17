Reddit Parser
==========

This is an API for collecting data from www.reddit.com. The best articles of the month are parsed
here. The result is a text file that contains the following information
for each post:

* unique numeric identifier of the record
* the name of user who posted
* user carma - is the grade you can get for posting and commenting on Reddit
* cake day - user account creation date
* post carma - the total amount of carma you have earned on all submissions, text or link
* comment carma - number of helpful comments
* publication date
* number of comments
* number of votes
* post category

The output file contains 100 records. This API also ignores posts
that do not match the following conditions:

* the post is posted and the user who posted it is deleted
* page content is not available without age verification
* fails to collect data in the right format and to the fullest extent
Installation / Requirements
---------------------------
For the application to work you need to install Google Chrome (if not) and download chromedriver from the website: https://chromedriver.chromium.org/downloads

The chromedriver version is selected to match the Google Chrome version. The downloaded chromedriver must be placed in the ``resources`` folder of the project.

1) Download and install python from the official website: https://www.python.org/downloads/

2) Enter at the command prompt ``git clone`` and go to this folder:

.. code-block:: shell

    > git clone https://github.com/jenkass/reddit_parser.git
    > cd reddit_parser

3) Create a new virtual environment inside the directory:

.. code-block:: shell

    > python -m venv 'name a virtual environment'

4) You must activate the virtual environment by typing at the command prompt:

.. code-block:: shell

    > 'name a virtual environment'\Scripts\activate.bat

5) Install third-party libraries in the virtual environment, using a ``requirements.txt``:

.. code-block:: shell

    > python -m pip install -r requirements.txt

6) Run the script:

.. code-block:: shell

    > python parser.py

Result
---------------------------
After the script runs, the project directory will contain a resulting text file named ``reddit-YYYYMMDDHHMM.txt``, where YYYY - year; MM - month; DD - day; HH - hours; mm - minutes
