This is code accompanying the following paper:

Paul Cook. Using social media to find English lexical blends. To
appear in Proceedings of the 15th EURALEX International Congress
(EURALEX 2012), Oslo, Norway.

Requirements:

langid.py: https://github.com/saffsd/langid.py

A Twitter account: https://twitter.com/

To build a collection of lexical blend candidates:

First edit collecttweets.bash appropriately.

Then to collect tweets run this:

$ bash ~/projects/blendid/scripts/collecttweets.bash

This will create a bunch of files with names like this:
120721072955.json (The filenames correpsond to the date and time the
process was started.) Each line of each file is a JSON string
representing a tweet.

Then once you've got a bunch of tweets, you can get the candidate
blends using this:

$ cat 120721072955.json | python tweetswithre.py --searchres=neos.re | python getblendinterpcands.py --lexfname=aspell_list.txt.gz 

Each line of the output has the following information
blend_candidate source_word1 source_word2 Regex_match URL_of_tweet text_of_tweet
=======