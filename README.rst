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
