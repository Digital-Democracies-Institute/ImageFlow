import pandas as pd
import json
import os
import numpy as np

def remove_retweets(df):
    print("Removing Twitter retweets...")
    print("Before removal of Retweets")
    print(df)

    df['group'] = df['group'].fillna(df['hashtags'])
    # print("after removal of twitter with no hashtags:")
    # print(df)

    df = pd.DataFrame(df)

    df['datetime'] = pd.to_datetime(df.datetime)
    #df['time'] = pd.to_datetime(df.time)
    #df['platform_with_groups'] = df['socialmedia'] + "/" + df['group']

    df = df.sort_values(["hashtags","cluster","datetime"], ascending=[True, True, False])

    #df.to_csv("resorted.csv", index=False)

    df.to_csv("added_new_cols.csv", index=False)

    CsvFile = 'added_new_cols.csv'
    df = pd.read_csv(CsvFile)

    df['next_cluster'] = df.cluster.shift(-1, fill_value=0)
    df['next_hashtags'] = df.hashtags.shift(-1)
    # for if cluster is the same and social media changes: add 1 weight.
    output = []

    count = 0
    out_count = 0
    for index, row in df.iterrows():
        count += 1
        orig_cluster = int(row['cluster'])
        next_cluster = int(row['next_cluster'])
        filename = str(row['FileName'])
        #socialmedia = str(row['socialmedia'])
        #platform_groups = str(row['platform_with_groups'])
        username = str(row['UserName'])
        datetime = str(row['datetime'])

        orig_hashtags = row['hashtags']
        next_hashtags = row['next_hashtags']

        if orig_cluster == next_cluster and orig_hashtags is not next_hashtags:
            out_count += 1
            row = {"cluster": orig_cluster, "FileName": filename, "hashtags": orig_hashtags, "UserName": username,
                   "datetime": datetime}
            #print(row)
            try:
                output.append(row)
            except Exception as ex1:
                print("unable to append to output")
        elif orig_cluster != next_cluster:
            row = {"cluster": orig_cluster, "FileName": filename, "hashtags": orig_hashtags, "UserName": username,
                   "datetime": datetime}
            try:
                output.append(row)
            except Exception as ex1:
                print("unable to append to output")

    print("count is " + str(out_count))
    df2 = pd.DataFrame(output)
    df2 = df2.sort_values(["cluster", "datetime"], ascending=[True, True])
    print("AFTER REMOVAL OF RETWEETS")
    print(df2)
    #os.remove(CsvFile)
    return df2


def main():
    filepath = "twitter_Reduced_final_with_retweets.csv"
    df = pd.read_csv(filepath)
    df = remove_retweets(df)
    df.to_csv('twitter_reduced_no_retweets.csv')


if __name__ == "__main__":
        main()