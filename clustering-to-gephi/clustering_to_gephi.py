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
    #pd_dataframe.to_csv("clustering.csv")
    return(pd_dataframe)

def multiplatform_filter(dataframe):
    print("Filtering out any cluster that does not cross platforms...")

    df2 = dataframe.drop_duplicates(["cluster", "socialmedia"])
    df = df2.groupby('cluster')['socialmedia'].agg(size= len, set= lambda x: set(x))
    single_platforms = df[df['size'] == 1]
    multi_platforms = df[df['size'] > 1]


    #TODO: Append to single_platforms.csv if the file exists.
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
    #output.to_csv("merge.csv")
    print(output)
    return output

def date_check(df):
    df2 = df['datetime'].isnull().values.sum()
    print("Checking if there are any invalid or missing dates...")
    print("There are " + str(df2) + " files missing dates.")

    rm_dates = input("Would you like to remove files with missing dates? (Yes/No) ")
    print("Remove dates is " + rm_dates)
    if rm_dates == 'Yes':

        print("Removing dates...")
        df = pd.DataFrame(df)
        no_date_df = df[df['datetime'].isnull()]
        no_date_df = pd.DataFrame(no_date_df)
        no_date_df.to_csv("removed_rows_with_no_date.csv", index=False)
        print("The no_date_df")
        print(no_date_df)

        df = df[df['datetime'].notna()]
        print(df)

        print("Multiplatform is on " + filter)

        if filter == 'Yes':

            print("Automatically re-checking for presence of single-platform clusters due to recently deleted rows...")
            df = multiplatform_filter(df)

    return df

def remove_clusters(df):
    # print("Enter the cluster numbers that you would like to remove: ")
    # try:
    #     cluster_list = []
    #     while True:
    #         cluster_list.append(int(input()))
    # except:
    #     print(cluster_list)
    #
    cluster_list = [3736, 7614, 2337, 3277, 468, 1928, 2973, 5992, 6828, 1357, 2765, 4142, 5398, 5647, 6365, 6442, 6876, 8356, 8416]

    for i in cluster_list:
        df.drop(df[df['cluster'] == i].index, inplace=True)

    return df

def memes_filter(df):
    not_memes_list = [2926, 2166, 1754, 1889, 2209, 2446, 3858, 4317, 6876, 23, 6, 114, 60, 206, 507, 282, 76, 267, 324, 153, 886, 13, 735, 385, 1182, 817, 2283, 194, 469, 1004, 630, 200, 257, 963, 786, 591, 730, 1950, 77, 292, 489, 700, 632, 940, 1360, 351, 3736, 231, 819, 19, 320, 3814, 56, 562, 1319, 5491, 444, 678, 4174, 1442, 4618, 301, 946, 1299, 1795, 2998, 3516, 3349, 4045, 445, 1447, 1864, 2703, 3620, 4416, 615, 984, 1152, 2898, 2947, 3419, 659, 1536, 2128, 3267, 3694, 3928, 5152, 5538, 105, 3127, 3312, 3653, 3677, 3945, 3991, 4818, 5809, 7059, 944, 1900, 2007, 2341, 3360, 4446, 277, 1243, 2099, 2747, 3070, 3087, 4089, 4413, 4453, 4680, 4917, 5129, 5580, 5619, 5669, 7040, 7367, 7379, 7765, 1015, 1042, 1091, 1690, 1839, 1902, 1928, 1935, 2031, 2042, 2098, 2726, 2827, 2993, 3133, 3166, 3175, 3490, 3545, 3808, 3822, 4108, 4125, 4177, 4284, 4399, 4782, 5447, 5541, 6100, 6117, 6240, 6562, 6739, 7075, 7220, 7504, 7550, 7645, 7892, 7920, 482, 580, 688, 719, 1024, 1394, 1557, 1582, 1603, 1605, 1622, 1658, 1808, 1978, 1992, 2054, 2102, 2108, 2239, 2281, 2469, 2673, 2732, 2765, 2800, 2975, 3172, 3224, 3276, 3301, 3308, 3503, 3650, 3927, 4052, 4117, 4198, 4204, 4206, 4207, 4217, 4384, 4508, 4623, 4712, 4714, 4786, 4798, 4899, 4906, 5021, 5040, 5213, 5342, 5362, 5409, 5431, 5462, 5470, 5674, 5693, 5854, 5881, 5966, 6006, 6008, 6041, 6057, 6114, 6206, 6393, 6467, 6578, 6629, 6693, 6718, 6719, 6756, 6827, 6906, 6944, 6955, 6957, 7010, 7081, 7199, 7219, 7227, 7317, 7334, 7342, 7369, 7399, 7471, 7492, 7493, 7548, 7595, 7638, 7689, 7774, 7819, 7919, 7991, 8008, 8079, 8099, 8127, 8232, 8269, 8329, 8331, 8360, 8361, 8385, 8410, 8416, 8483, 8486, 8487, 8491, 8508, 3104]

    for i in not_memes_list:
        df.drop(df[df['cluster'] == i].index, inplace=True)

    return df


def directional_gephi(df):
    df['next_cluster'] = df.cluster.shift(-1, fill_value=0)
    df['next_socialmedia'] = df.platform_with_groups.shift(-1)
    df['next_platform'] = df.socialmedia.shift(-1)

    # for if cluster is the same and social media changes: add 1 weight.
    output = []

    count = 0
    out_count = 0
    for index, row in df.iterrows():
        count += 1
        orig_cluster = int(row['cluster'])
        next_cluster = int(row['next_cluster'])

        orig_platform = row['socialmedia']
        next_platform = row['next_platform']

        orig_social = row['platform_with_groups']
        next_social = row['next_socialmedia']


        #if orig_cluster == next_cluster and orig_social is not next_social:
        if orig_cluster == next_cluster and orig_platform is not next_platform:
            out_count += 1
            #row = {"cluster": orig_cluster, "source": orig_social, "platform":orig_platform, "target": next_social, "next_platform":next_platform, "weight": "1"}
            row = {"cluster": orig_cluster, "source": orig_platform, "target": next_platform, "weight": "1"}
            try:
                output.append(row)
            except Exception as ex1:
                print("unable to append to output")
        elif orig_cluster != next_cluster:
            #print("Changing to the next cluster from " + str(orig_cluster) + " to " + str(next_cluster))
            continue

    df = pd.DataFrame(output)

    df.to_csv('final_gephi.csv', index=False)

    # Adding weight sums together
    source_file = "final_gephi.csv"

    #TODO: Not working
    #df2 = pd.read_csv(source_file)

    # df_sum = df2.groupby(['source', 'target']).sum()
    #
    # df_sum.to_csv('final_gephi_sum.csv')


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
    print("AFTER REMOVAL OF RETWEETS")
    print(df2)
    #os.remove(CsvFile)
    return df2

def groupby(df):
    df2 = df.groupby(['cluster']).size()
    df2.to_csv('final_groupby_count.csv')

    df = df.drop_duplicates(["cluster", "socialmedia"])
    df = df.groupby(['cluster']).agg(lambda x: x.tolist())
    df.to_csv('final_groupby.csv')

def main():
    ##file_path = input("Let's get started. Add the filepath of your clustering_output.txt here:")
    ##alternative to manually add file_path here and not use UI
    file_path = "clustering_output_identicals.txt"
    pd_dataframe = convert_to_df(file_path)
    print(pd_dataframe)

    merge = input("Would you like to merge your data with a csv of corresponding metadata? (Yes/No) ")
    if merge == 'Yes':
        #merge_file = input("What is the filepath to the metadata csv file?")
        merge_file = '/Volumes/Elsa_HD2/Memes/data/All-Metadata/all_metadata.csv'
        pd_dataframe = metadata_merge(pd_dataframe, merge_file)

    pd_dataframe = date_check(pd_dataframe)

    pd_dataframe.to_csv("original_postMerge.csv")
    global filter
    filter = input("Would you like to filter for only multi-platform clusters? (Yes/No) ")
    if filter == 'Yes':
        pd_dataframe = multiplatform_filter(pd_dataframe)
        print(pd_dataframe)


    rm_clusters = input("Would you like to remove specific cluster(s) from the data? (Yes/No) ")
    if rm_clusters == 'Yes':
        pd_dataframe = remove_clusters(pd_dataframe)

    if filter and rm_clusters:
        memes = input("Would you like to filter for only memes?")
        if memes:
            memes_filter(pd_dataframe)
  #  pd_dataframe = multiplatform_filter(pd_dataframe)

    # groupby(pd_dataframe)

    #TODO: The remove_retweets needs the dataframe to have an attribute 'datetime'
    rm_retweets = input("Would you like to remove twitter retweets from the data? (Yes/No) ")
    if rm_retweets == 'Yes':
        pd_dataframe = remove_retweets(pd_dataframe)

    pd_dataframe.to_csv("final.csv", index=False)
    groupby(pd_dataframe)

    gephi = input("Would you like to create a gephi-formatted csv? (Yes/No) ")
    if gephi == 'Yes':
        directional_gephi(pd_dataframe)

    # df = pd.read_csv('multiplatform-noretweets-allimages/final.csv')
    # directional_gephi(df)
    # df = remove_retweets(df)
   # df.to_csv("final.csv", index=False)
    #
    # groupby(df)


if __name__ == "__main__":
    main()