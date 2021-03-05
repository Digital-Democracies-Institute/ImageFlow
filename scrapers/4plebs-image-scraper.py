#4Plebs API Documentation found here: https://4plebs.tech/foolfuuka/#4plebs-specific-boards-information

import os
import wget
import urllib.request
import json
import requests
import pandas as pd
import csv
import time


def scrape_4chan(start, end, group, country_code):

    # CHANGE THESE SETTINGS!
    counter = 0
    total_posts = 0
    output_df = []

    # USER INPUTS
    # start = "2019-10-14" #Sept 1, 2019
    # end = '2019-10-21' #Nov 30, 2019
    # group = 'pol'   #group aka board_url
    # country_code = 'CA' #country code unique to 4chan

    current_page = 0

    #TODO: What filesystem should we use for our database?
    saveDirectory = "cedar/database/4chan"
    print("The current working directory is " + saveDirectory)
    path = saveDirectory + "/" + group

    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed  - possible directory already exists" % path)
    else:
        print("Successfully created the directory %s" % path)


    # Get the 4chan board catalog JSON file and open it
    base_url = "https://archive.4plebs.org/_/api/chan/search/?boards="+ group + "&start="+ start +"&end=" + end + "&country=" + country_code + "&page=" + str(current_page)
    print(base_url)

    result = requests.get(base_url)
    result.raise_for_status()
    print(result.text)
    result = json.loads(result.text)["0"]["posts"]

    pd_result = pd.json_normalize(result)
    df = pd.DataFrame(pd_result)
    print(df)

    while current_page != None:

        base_url = "https://archive.4plebs.org/_/api/chan/search/?boards=" + group + "&start=" + start + "&end=" + end + "&country=" + country_code + "&page=" + str(current_page)
        print(base_url)
        time.sleep(20)

        result = requests.get(base_url)
        result.raise_for_status()
        result = json.loads(result.text)["0"]["posts"]

        pd_result = pd.json_normalize(result)
        df = pd.DataFrame(pd_result)

        for i in range(0, len(df)):
            total_posts += 1
            try:
                image_url = df['media.media_link'][i]
                print(image_url)
            except Exception as ex_media:
                print("No media.media_link.")

            try:
                #download image file to database folder
                file_name = wget.download(image_url, path)
                counter += 1

                try:
                    username = df['name'][i]
                    timestamp = df['timestamp'][i]
                    country = df['poster_country_name'][i]

                    filename = df['media.media'][i]
                    group_name = df['board.shortname'][i]

                    row = {"FileName": file_name, "Url": image_url, "group": group_name, "timestamp": timestamp, "country":country}
                    output_df.append(row)

                except Exception as ex1:
                    print("Could not retrieve info.")

            except Exception as ex:
                print("URL not found")

            print(str(counter) + " images successfully downloaded from page " + str(current_page) + ".")
            print("...")
            print("Total posts searched: " + str(total_posts))

        current_page += 1

    # Output is Pandas Dataframe
    df = pd.DataFrame(output_df)

    print("Total posts searched: " + str(total_posts))
    print("Script completed")
