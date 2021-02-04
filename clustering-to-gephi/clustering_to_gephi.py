import pandas as pd
import json
import os
import numpy as np

#global variable for multi-platform filter
filter = 'no'

# Borrowed method to parse absolute and relative paths
def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def convert_to_df(file_path):
    print("Converting to CSV")
    print(file_path)
    output = []

    with open(file_path, 'r') as f:
        for line in f:
            output_json = json.loads(line)
            images_in_cluster = output_json['images']
            cluster = output_json['cluster_no']

            for i in images_in_cluster:
                #TODO: This will need to be adjusted when used in ComputeCanada
                socialmedia = splitall(i)
                socialmedia = socialmedia[5]
                filename = splitall(i)
                filename = filename[-1]
                z = {"cluster": cluster, "FileName": filename, "images": i, "socialmedia": socialmedia}

                output.append(z)

    pd_dataframe = pd.DataFrame(output)
    pd_dataframe = pd_dataframe.drop_duplicates(subset='images')
    pd_dataframe.to_csv("clustering.csv")
    return(pd_dataframe)

def multiplatform_filter(dataframe):
    print("Filtering out any cluster that does not cross platforms...")

    df2 = dataframe.drop_duplicates(["cluster", "socialmedia"])
    df = df2.groupby('cluster')['socialmedia'].agg(size= len, set= lambda x: set(x))
    single_platforms = df[df['size'] == 1]
    multi_platforms = df[df['size'] > 1]

    single_platforms = pd.DataFrame(single_platforms)
    multi_platforms = pd.DataFrame(multi_platforms)
    single_cluster_list = single_platforms.index.values.tolist()
    output_single = []

    print("Scanning files...")

    output_single.append(dataframe.loc[dataframe['cluster'].isin(single_cluster_list)])
    single_df = pd.DataFrame(np.concatenate(output_single))
    single_df= single_df.rename(columns={0:"cluster", 1:"FileName", 2:"images", 3:"socialmedia", 4:"URL", 5:"SocialMedia", 6:"BoardName", 7:"group", 8:"hashtags", 9:"UserName", 10:"TimeStamp", 11:"date", 12:"time", 13:"datetime"})
    single_df.to_csv("single_platforms.csv", index=False)

    multi_cluster_list = multi_platforms.index.values.tolist()
    output_multi = []
    output_multi.append(dataframe.loc[dataframe['cluster'].isin(multi_cluster_list)])
    multi_df = pd.DataFrame(np.concatenate(output_multi))
    multi_df = multi_df.rename(
        columns={0: "cluster", 1: "FileName", 2: "images", 3: "socialmedia", 4: "URL", 5: "SocialMedia", 6: "BoardName",
                 7: "group", 8: "hashtags", 9: "UserName", 10: "TimeStamp", 11: "date", 12: "time", 13:"datetime"})

    multi_df.to_csv("multi_platforms.csv", index=False)

    return multi_df

def metadata_merge(df, merge_file):
    df_merge = pd.read_csv(merge_file)
    print("Merging files...")
    output = pd.merge(df, df_merge, on='FileName', how='left')
    print("Merging at the filename...")
    output = output[output['socialmedia'].notna()]
    output = output.drop_duplicates(subset='images')
    output.to_csv("merge.csv")
    print(output)
    return output

def date_check(df):
    df2 = df['date'].isnull().values.sum()
    print("Checking if there are any invalid or missing dates...")
    print("There are " + str(df2) + " files missing dates.")

    rm_dates = input("Would you like to remove files with missing dates? (Yes/No) ")
    print("Remove dates is " + rm_dates)
    if rm_dates == 'Yes':

        print("Removing dates...")
        df = pd.DataFrame(df)
        no_date_df = df[df['date'].isnull()]
        no_date_df = pd.DataFrame(no_date_df)
        no_date_df.to_csv("removed_rows_with_no_date.csv", index=False)
        print("The no_date_df")
        print(no_date_df)

        df = df[df['date'].notna()]
        print(df)

        print("Multiplatform is on " + filter)

        if filter == 'Yes':

            print("Automatically re-checking for presence of single-platform clusters due to recently deleted rows...")
            df = multiplatform_filter(df)

    return df

def remove_clusters(df):
    print("Enter the cluster numbers that you would like to remove: ")
    try:
        cluster_list = []
        while True:
            cluster_list.append(int(input()))
    except:
        print(cluster_list)

    for i in cluster_list:
        df.drop(df[df['cluster'] == i].index, inplace=True)

    return df

def remove_retweets(df):
    print("Removing Twitter retweets...")

    df['group'] = df['group'].fillna(df['hashtags'])

    df = pd.DataFrame(df)

    df['datetime'] = pd.to_datetime(df.datetime)
    #df['time'] = pd.to_datetime(df.time)
    df['platform_with_groups'] = df['socialmedia'] + "/" + df['group']

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
        socialmedia = str(row['socialmedia'])
        platform_groups = str(row['platform_with_groups'])
        username = str(row['UserName'])
        datetime = str(row['datetime'])

        orig_hashtags = row['hashtags']
        next_hashtags = row['next_hashtags']

        if orig_cluster == next_cluster and orig_hashtags is not next_hashtags or socialmedia != "twitter":
            out_count += 1
            row = {"cluster": orig_cluster, "FileName": filename, "socialmedia": socialmedia,
                   "platform_with_groups": platform_groups, "hashtags": orig_hashtags, "UserName": username,
                   "datetime": datetime}
            #print(row)
            try:
                output.append(row)
            except Exception as ex1:
                print("unable to append to output")
        elif orig_cluster != next_cluster:
            row = {"cluster": orig_cluster, "FileName": filename, "socialmedia": socialmedia,
                   "platform_with_groups": platform_groups, "hashtags": orig_hashtags, "UserName": username,
                   "datetime": datetime}
            try:
                output.append(row)
            except Exception as ex1:
                print("unable to append to output")

    print("count is " + str(out_count))
    df2 = pd.DataFrame(output)
    df2 = df2.sort_values(["cluster", "datetime"], ascending=[True, True])
    print(df2)
    return df2


def main():
    # file_path = input("Let's get started. Add the filepath of your clustering_output.txt here:")
    # alternative to manually add file_path here and not use UI
    file_path = "clustering_output_identicals.txt"
    pd_dataframe = convert_to_df(file_path)
    print(pd_dataframe)

    merge = input("Would you like to merge your data with a csv of corresponding metadata? (Yes/No) ")
    if merge == 'Yes':
        #merge_file = input("What is the filepath to the metadata csv file?")
        merge_file = '/Volumes/Elsa_HD2/Memes/data/All-Metadata/all_metadata.csv'
        pd_dataframe = metadata_merge(pd_dataframe, merge_file)

    pd_dataframe = date_check(pd_dataframe)

    global filter
    filter = input("Would you like to filter for only multi-platform clusters? (Yes/No) ")
    if filter == 'Yes':
        pd_dataframe = multiplatform_filter(pd_dataframe)
        print(pd_dataframe)

    rm_clusters = input("Would you like to remove specific cluster(s) from the data? (Yes/No) ")
    if rm_clusters == 'Yes':
        pd_dataframe = remove_clusters(pd_dataframe)

    pd_dataframe = multiplatform_filter(pd_dataframe)

    rm_retweets = input("Would you like to remove twitter retweets from the data? (Yes/No) ")
    if rm_retweets == 'Yes':
        pd_dataframe = remove_retweets(pd_dataframe)

    pd_dataframe.to_csv("final.csv", index=False)



if __name__ == "__main__":
    main()