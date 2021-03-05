from datetime import datetime
from psaw import PushshiftAPI
import wget
import os
#import datetime
import subprocess
import pandas as pd

# Easy conversion for date to UNIX timestamps here: https://www.unixtimestamp.com/index.php

# Connect to PushShift API
try:
    api = PushshiftAPI()
except Exception as ex1:
    print("unable to connect to PushShift")

output = []

#local_path = os.getcwd()
local_path = "cedar/database/reddit"

# USER INPUT SUBREDDIT LIST AND START AND END DATE CONVERTED TO TIMESTAMP
sub_list = ['canada', 'canadaleft', 'canadapolitics', 'canadapoliticshumour', 'canadianpolitics', 'lpc', 'metacanada', 'ndp', 'onguardforthee', 'piratepartyofcanada']

after = '1567296000' #Sept 1, 2019
before = '1575158340' #Nov 30, 2019


curr_date = str(datetime.date(datetime.now()))
curr_date = curr_date.replace('-','')

brokenImageLinks = 0
counter = 0

for subreddit in sub_list:
    print("Scraping images in "+str(subreddit)+" begins...")
    print("...")

    try:
        meme_list = list(api.search_submissions(subreddit=str(subreddit), filter=['url', 'author', 'created_utc', 'score', 'num_comments'], after=str(after), before=str(before)))


    except Exception as search_Except:
        print("unable to make query through pushShift")

    #create folders for each subreddit
    day_dir = local_path + "Reddit/"+str(subreddit)+ "/" + curr_date

    try:
        os.mkdir(day_dir)
    except OSError:
        print ("Creation of the directory %s failed" % day_dir)
    else:
        print ("Successfully created the day directory %s " % day_dir)


    for meme in meme_list:
        #scrapes jpg, gif, and png
        if (str(meme.url).endswith('.jpg') or str(meme.url).endswith('.gif') or str(meme.url).endswith('.jpeg') or str(meme.url).endswith('.png')):

            counter += 1

            #and not str(meme.url).startswith('https://i.imgflip.com')
            print(meme.url)

            redditScore = str(meme.score)
            numCmts = str(meme.num_comments)

            try:
                file_name = wget.download(meme.url,day_dir)

                # ////PUT IN SEPARATE FUNCTION /////
                unixTime = meme.created_utc
                timestamp = str(unixTime)
                # convertDate = datetime.fromtimestamp(int(unixTime)).strftime('%Y-%m-%d')
                # convertTime = datetime.fromtimestamp(int(unixTime)).strftime('%H:%M:%S')
                # print("TIMESTAMP: " + timestamp)
                # print(convertDate)
                # print(convertTime)

                # redditScore and NumComments are added as strings not int
                try:
                    #TODO: instead of exiftool tags create DF with tags

                    subprocess.check_call(['exiftool', '-RedditPostDate='+convertDate, '-RedditUser=' + meme.author,
                                           '-Subreddit=' + subreddit, '-RedditPostTime=' + convertTime,
                                           '-RedditScore=' + redditScore, '-RedditNumCmts=' + numCmts, '-TimeStamp=' + timestamp,"-overwrite_original_in_place", file_name])


                except Exception as ex1:
                    print("DF creation failed")



            except Exception as ex:
                print("Image URL Broken. Could not download.")
                try:
                    #Included to fix issue with downloading imgflip images
                    print("Trying again via Terminal command line...")

                    subprocess.check_call(['wget', meme.url, '-P', day_dir], timeout=60)

                    full_url = meme.url
                    file_name = full_url.rsplit('/', 1)[-1]
                    full_path = day_dir + file_name

                    # ////PUT IN SEPARATE FUNCTION /////
                    unixTime = meme.created_utc
                    convertDate = datetime.fromtimestamp(int(unixTime)).strftime('%Y-%m-%d')
                    convertTime = datetime.fromtimestamp(int(unixTime)).strftime('%H:%M:%S')
                    print(convertDate)
                    print(convertTime)

                    #get resulting path of that file
                    #file_name = day_dir +

                    # redditScore and NumComments are added as strings not int
                    try:
                        #command = "exiftool -RedditPostDate=" + convertDate + " -RedditUser=" + meme.author + " -Subreddit=" + subreddit + " -RedditPostTime=" + convertTime + " -RedditScore=" + redditScore + " -RedditNumCmts=" + numCmts + " " + full_path

                        subprocess.check_call(['exiftool', '-RedditPostDate=' + convertDate, '-RedditUser=' + meme.author,
                                        '-Subreddit=' + subreddit, '-RedditPostTime=' + convertTime,
                                        '-RedditScore=' + redditScore, '-RedditNumCmts=' + numCmts, '-TimeStamp=' + timestamp, "-overwrite_original_in_place", full_path])

                       # subprocess.call([command])
                    except subprocess.CalledProcessError as ex1:
                        print("OS unix command failed")

                     #//////////////////////////////////
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as ex2:
                    print("Second attempt to download url failed.")
                    brokenImageLinks+=1

            print("\n")


    print("...")

print("Total Broken Image Links: "+str(brokenImageLinks))
print("Total attempted image posts: "+str(counter))

