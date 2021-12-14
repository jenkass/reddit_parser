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

The result is written to one of the databases: ``MongoDB`` or ``PostgreSQL``. This application also ignores posts
that do not match the following conditions:

* the post is posted and the user who posted it is deleted
* page content is not available without age verification
* fails to collect data in the right format and to the fullest extent

REST API Service
---------------------------
This is a Restful service that provides an API to handle CRUD operations on a databases.
It runs on ``http://localhost:8087/``. The server saves the result in databases: ``MongoDB`` or ``PostgreSQL``.

List of service methods and endpoints:

* ``GET http://localhost:8087/posts/`` - returns the contents of the entire database in JSON format

* ``GET http://localhost:8087/posts/<UNIQUE_ID>/`` - returns the contents of the string (document) with the ``UNIQUE_ID``

* ``POST http://localhost:8087/posts/`` - adds a new line (document) to the database, creates a new table (collection) if the table (collection) does not exist, checks the content of the table (collection) for the absence of duplicates in the ``UNIQUE_ID`` field before creating the line (document), in case of success it returns the operation code ``201``, as well as the JSON format ``{""UNIQUE_ID"": the number of the inserted line (document)}``

* ``DELETE http://localhost:8087/posts/<UNIQUE_ID>/`` - deletes the line (document) of the table (collection) with the ``UNIQUE_ID``

* ``PUT http://localhost:8087/posts/<UNIQUE_ID>/`` - changes the contents of the table (collection) string (document) with the ``UNIQUE_ID``

Unless otherwise specified, all requests return code ``200`` if successful; those referring to a line (document) number return ``404``
if no line (document) with the requested number is found. Unless otherwise specified, the response content is empty.

Docker
---------------------------
Docker is used to run the database servers.
You need to download it from the official website https://www.docker.com/products/docker-desktop and install it on your computer.

Docker compose
---------------------------
Create a Docker-compose file - ``name_file.yaml`` with the following contents:

.. code-block:: shell

    version: '3'
    services:
        mongodb:
            image: mongo
            ports:
                - "`port_your_local_machine`:27017"
            environment:
                - MONGO_INITDB_ROOT_USERNAME=`your_username`
                - MONGO_INITDB_ROOT_PASSWORD=`your_password`
            volumes:
                - mongo-data:/data/db
        postgres:
            image: postgres
            ports:
                - "`port_your_local_machine`:5432"
            restart: always
            environment:
                - POSTGRES_PASSWORD=`your_password`
                - POSTGRES_USER=`your_username`
                - POSTGRES_DB=`your_name_database`
            volumes:
                - postgre-data:/var/lib/postgresql/data
    volumes:
        mongo-data:
            driver: local
        postgre-data:
            driver: local

Where you need to insert your parameters:

    - ``port_your_local_machine``: the host on which the database will run
    - ``your_username``: username username
    - ``your_password``: password to connect to the database
    - ``your_name_database``: database name

To start Docker-compose in the terminal, type:

.. code-block:: shell

    > docker compose -f `file_name`.yaml up

After that, the appropriate images will be downloaded and all server database containers will run.

MongoDB
---------------------------
To connect the database to the project, you need:

    In the CLUSTER variable, write the database connection string, such as ``"mongodb://`user`:`password`@localhost:27017"``.
    where ``user`` is the database user name,
    ``password`` - password for connection.
    These parameters were specified in the ``Docker-compose`` file.

The database will have 2 collections: ``posts`` and ``users``.

Collections will be created when inserting data, if there is no collection, if a user with the passed name already exists, then adding a new document to the ``users`` collection will not happen.
When deleting a post, if there are no other posts with that user, the user will be deleted from the ``users`` collection.


PostgreSQL
---------------------------
To connect to a PostgreSQl server, you must:

    In the postgredb file set the ``USER``, ``PASSWORD``, ``DB_NAME`` variables to write the values that you specified in the ``Docker-compose`` file.

The database will have 2 tables: ``posts`` and ``users``.

When inserting data, if there are no tables, they will be created and the data will be inserted into them. If a user with this name already exists, the data inserted into the Users table will be ignored.
When deleting a post, if there are no posts with the same user, the user from the Users table will be deleted.


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

6) Start Docker-compose. The startup process is described above.

7) Run the server

   To select the resulting database, you must specify the optional parameter ``-db`` and the name of the database ``mongo`` or ``postgre``.
   By default, the database is selected ``mongo``

.. code-block:: shell

    > python -m REST_API_Server.server
    Example:
    > python -m REST_API_Server.server -db 'mongo'
    > python -m REST_API_Server.server -db 'postgre'

8) Run the script on another command line.

   If you want to set the number of posts for parsing,
   you must specify the optional argument ``-cp`` and specify the number of posts.

   If you do not specify optional arguments, the default value for the number of posts = 1000.

.. code-block:: shell

    > python parser.py
    Example:
    > python parser.py -cp 50

To terminate the server, press ``CTRL-C`` at the command line where the server was started.

Result
---------------------------
Based on your choice of database, the results will be recorded in one of the items:

1) If you chose ``MongoDB``, the results will be on cloud storage, where the database server resides in two collections: ``posts`` and ``users``
2) If you choose ``PostgreSQL``, the results will be on your local database server in two tables:``posts`` and ``users``
