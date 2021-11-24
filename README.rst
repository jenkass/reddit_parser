Reddit Parser with REST API
==========

This is an application for collecting data from www.reddit.com. The best articles of the month are parsed
here. The received data is formed into a json object and sent by POST method to the server. This object contains
the following information for each post:

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

The output file contains 100 records. This application also ignores posts
that do not match the following conditions:

* the post is posted and the user who posted it is deleted
* page content is not available without age verification
* fails to collect data in the right format and to the fullest extent

REST API Service
---------------------------
This is a Restful service that provides an API to handle CRUD operations on a file.
It runs on ``http://localhost:8087/``. The server saves the result in a text file
named ``reddit-YYYYYMMDD.txt`` where YYYY - year; MM - month; DD - day.

List of service methods and endpoints:

* ``GET http://localhost:8087/posts/`` - returns the contents of the entire file in JSON format

* ``GET http://localhost:8087/posts/<UNIQUE_ID>/`` - returns the contents of the string with the ``UNIQUE_ID``

* ``POST http://localhost:8087/posts/`` - adds a new line to the file, creates a new one if the file does not exist, checks the content of the file for the absence of duplicates in the ``UNIQUE_ID`` field before creating the line, in case of success it returns the operation code ``201``, as well as the JSON format ``{""UNIQUE_ID"": the number of the inserted line}``

* ``DELETE http://localhost:8087/posts/<UNIQUE_ID>/`` - deletes the line of the file with the ``UNIQUE_ID``

* ``PUT http://localhost:8087/posts/<UNIQUE_ID>/`` - changes the contents of the file string with the ``UNIQUE_ID``

Unless otherwise specified, all requests return code ``200`` if successful; those referring to a line number return ``404``
if no line with the requested number is found. Unless otherwise specified, the response content is empty.


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

6) Run the server

.. code-block:: shell

    > python server.py

7) Run the script on another command line.

   If you want to set the number of posts for parsing,
   you must specify the optional argument ``-cp`` and specify the number of posts.

   If you do not specify optional arguments, the default value for the number of posts = 100.

.. code-block:: shell

    > python parser.py
    Example:
    > python parser.py -cp 50

To terminate the server, press ``CTRL-C`` at the command line where the server was started.

Result
---------------------------
After the parser sends all post data to the server, the server will save everything to a text file named ``reddit-YYYYMMDD.txt``,
where YYYY - year; MM - month; DD - day. To further manipulate the data, you can use the ``POSTMAN`` application and
send various methods with the endpoints listed above.
