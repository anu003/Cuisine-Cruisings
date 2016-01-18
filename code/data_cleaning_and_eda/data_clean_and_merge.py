"""
##### Clean the web scraped recipe data, combine data from all 6 recipe
##### sources, and store combined data in MongoDB and pickle file
"""

import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from pymongo import MongoClient
import pickle
from non_ascii_elements_and_stop_words import non_ascii_elements


# create MongoDB database and collection
DB_NAME = 'PROJECT_RECIPES'
COLLECTION_NAME = 'RECIPES_DATA'

# connect to mongodb to store cleaned, formatted and merged data
client = MongoClient()
db = client[DB_NAME]
coll = db[COLLECTION_NAME]


def save_obj(obj, name):
    """
    Dump object in pickel file in data folder
    :params  obj (object): object to be saved (can be in any form)
             name (str): file-name to save object with
    """
    with open('Data/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    """
    Load object from pickel file in data folder
    :param  name (str): file-name to load object from
    :return  object in original format
    """
    with open('Data/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def replace_all(text):
    """
    Replace all html encoded content in the data with their resspective ascii \
    encoded values (alphabets and symbols)
    Also remove any brackets from the data ('[]{}()')
    :param  text (str): text from recipe details dictionary in database
    :return  replaced ascii encodable text content in string format
    """

    # dictionary mapping of all the observed non-ascii html characters with \
    # their ascii encodable value, as well as the brackets
    vulgar_fraction_puctuation = non_ascii_elements()

    # loop over each to be replaced item (keys in dictionary) and replace all \
    # occurences in text with the corresponding value
    for old_value, new_value in vulgar_fraction_puctuation.iteritems():
        text = text.replace(old_value, new_value)
    # return text with all the non-ascii characters replaced
    return text


def convert_fractions_and_remove_brackets(data):
    """
    Convert all non-ascii occurences in recipe details dictionary
    :param  data (dictionary): dict of recipe details for one recipe
    :return  dictionary with all the non-ascii replaced with their \
                correspinding ascii values
    """

    # loop over all keys in recipe details dictionary
    for key_value in data:
        # if value corresponding to the key is a list, then create a list strings \
        # with non-ascii charachters replaced
        if type(data[key_value]) == list:
            new_list = []
            # loop over each of the list items and append the converted string to \
            # new_list
            for list_row in data[key_value]:
                new_list.append(replace_all(list_row))
            # reset the dic value with new_list
            data[key_value] = new_list
        # if value corresponding to key is unicode, then replace all non-ascii \
        # char and reset dict value
        if type(data[key_value]) == unicode:
            data[key_value] = replace_all(data[key_value])
    # return dictionary with non-ascii char replaced
    return data


def bbc_food_data():
    """
    Load bbc food data, replace non-ascii chars with their correspinding ascii \
    values and remove duplicates
    :param  none
    :return  pandas dataframe with all the non-ascii replaced and duplicates removed
    """

    # load data (which was in pandas format before we pickeling) from pickle \
    # and sort index
    bbc_data = load_obj('recipes_data_bbc_food').sort_index()
    # remove float indices
    bbc_data.reset_index(inplace=True)
    bbc_data.drop('index', axis=1, inplace=True)
    # replace non-ascii char with corresponding values
    bbc_data['recipes_details'] = map(convert_fractions_and_remove_brackets,
        bbc_data['recipes_details'])
    # insert columns 'recipe_tilte' and 'recipe_link' to dataframe
    bbc_data['recipe_title'] = map(lambda x: x['recipe title'],
        bbc_data['recipes_details'])
    bbc_data['recipe_link'] = map(lambda x: x['r_link'], bbc_data['recipes_details'])
    # use recipe_link and cuisine name to find and drop any duplicates
    bbc_data.drop_duplicates(['recipe_link', 'cuisine'], keep='first', inplace=True)
    # reset index after dropping duplictes
    bbc_data.reset_index(inplace=True)
    # drop 'index' and 'recipe_link' columns from dataframe
    bbc_data.drop(['index', 'recipe_link'], axis=1, inplace=True)

    # return cleaned data for bbc_food
    return bbc_data


def epicurious_data():
    """
    Load epicurious data, replace non-ascii chars with their correspinding ascii \
    values and remove duplicates
    :param  none
    :return  pandas dataframe with all the non-ascii replaced and duplicates removed
    """

    # load data (which was in pandas format before we pickeling) from pickle \
    # and sort index
    epicurious_data = load_obj('recipes_data_epicurious').sort_index()
    # remove float indices
    epicurious_data.reset_index(inplace=True)
    epicurious_data.drop('index', axis=1, inplace=True)
    # replace non-ascii char with corresponding values
    epicurious_data['recipes_details'] = map(convert_fractions_and_remove_brackets,
        epicurious_data['recipes_details'])
    # insert columns 'recipe_tilte' and 'recipe_link' to dataframe
    epicurious_data['recipe_title'] = map(lambda x: x['recipe title'],
        epicurious_data['recipes_details'])
    epicurious_data['recipe_link'] = map(lambda x: x['r_link'],
        epicurious_data['recipes_details'])
    # use recipe_link and cuisine name to find and drop any duplicates
    epicurious_data.drop_duplicates(['recipe_link', 'cuisine'],
        keep='first', inplace=True)
    # reset index after dropping duplictes
    epicurious_data.reset_index(inplace=True)
    # drop 'index' and 'recipe_link' columns from dataframe
    epicurious_data.drop(['index', 'recipe_link'], axis=1, inplace=True)
    # return cleaned data for epicurious
    return epicurious_data


def chowhound_data():
    """
    Load chowhound data, replace non-ascii chars with their correspinding ascii \
    values and remove duplicates
    :param  none
    :return  pandas dataframe with all the non-ascii replaced and duplicates removed
    """

    # load data (which was in pandas format before we pickeling) from pickle \
    # and sort index
    chowhound_data = load_obj('recipes_data_chowhound').sort_index()
    # remove float indices
    chowhound_data.reset_index(inplace=True)
    chowhound_data.drop('index', axis=1, inplace=True)
    # replace non-ascii char with corresponding values
    chowhound_data['recipes_details'] = map(convert_fractions_and_remove_brackets,
        chowhound_data['recipes_details'])
    # insert columns 'recipe_tilte' and 'recipe_link' to dataframe
    chowhound_data['recipe_title'] = map(lambda x: x['recipe title'],
        chowhound_data['recipes_details'])
    chowhound_data['recipe_link'] = map(lambda x: x['r_link'],
        chowhound_data['recipes_details'])
    # use recipe_link and cuisine name to find and drop any duplicates
    chowhound_data.drop_duplicates(['recipe_link', 'cuisine'], keep='first',
        inplace=True)
    # reset index after dropping duplictes
    chowhound_data.reset_index(inplace=True)
    # drop 'index' and 'recipe_link' columns from dataframe
    chowhound_data.drop(['index', 'recipe_link'], axis=1, inplace=True)
    # return cleaned data for chowhound
    return chowhound_data


def bbc_good_food_data():
    """
    Load bbc good food data, replace non-ascii chars with their correspinding ascii \
    values and remove duplicates
    :param  none
    :return  pandas dataframe with all the non-ascii replaced and duplicates removed
    """

    # load data (which was in pandas format before we pickeling) from pickle \
    # and sort index
    bbc_good_food_data = load_obj('recipes_data_bbc_good_food').sort_index()
    # remove float indices
    bbc_good_food_data.reset_index(inplace=True)
    bbc_good_food_data.drop('index', axis=1, inplace=True)
    # replace non-ascii char with corresponding values
    bbc_good_food_data['recipes_details'] = map(convert_fractions_and_remove_brackets,
        bbc_good_food_data['recipes_details'])
    # insert columns 'recipe_tilte' and 'recipe_link' to dataframe
    bbc_good_food_data['recipe_title'] = map(lambda x: x['recipe title'],
        bbc_good_food_data['recipes_details'])
    bbc_good_food_data['recipe_link'] = map(lambda x: x['r_link'],
        bbc_good_food_data['recipes_details'])
    # use recipe_link and cuisine name to find and drop any duplicates
    bbc_good_food_data.drop_duplicates(['recipe_link', 'cuisine'],
        keep='first', inplace=True)
    # reset index after dropping duplictes
    bbc_good_food_data.reset_index(inplace=True)
    # drop 'index' and 'recipe_link' columns from dataframe
    bbc_good_food_data.drop(['index', 'recipe_link'], axis=1, inplace=True)
    # return cleaned data for bbc_good_food
    return bbc_good_food_data


def saveur_data():
    """
    Load saveur data, replace non-ascii chars with their correspinding ascii \
    values and remove duplicates
    :param  none
    :return  pandas dataframe with all the non-ascii replaced and duplicates removed
    """

    # load data (which was in pandas format before we pickeling) from pickle \
    # and sort index
    saveur_data = load_obj('recipes_data_saveur').sort_index()
    # remove float indices
    saveur_data.reset_index(inplace=True)
    saveur_data.drop('index', axis=1, inplace=True)
    # replace non-ascii char with corresponding values
    saveur_data['recipes_details'] = map(convert_fractions_and_remove_brackets,
        saveur_data['recipes_details'])
    # insert columns 'recipe_tilte' and 'recipe_link' to dataframe
    saveur_data['recipe_title'] = map(lambda x: x['recipe title'],
        saveur_data['recipes_details'])
    saveur_data['recipe_link'] = map(lambda x: x['r_link'],
        saveur_data['recipes_details'])
    # use recipe_link and cuisine name to find and drop any duplicates
    saveur_data.drop_duplicates(['recipe_link', 'cuisine'], keep='first', inplace=True)
    # reset index after dropping duplictes
    saveur_data.reset_index(inplace=True)
    # drop 'index' and 'recipe_link' columns from dataframe
    saveur_data.drop(['index', 'recipe_link'], axis=1, inplace=True)
    # return cleaned data for saveur
    return saveur_data


def combine_data():
    """
    Clean data from all sources, merge the data to form a new pandas dataframe \
    :param  none
    :return  none
    """

    # get clean data from each source and append to new dataframe
    recipes_data = pd.DataFrame()
    recipes_data = recipes_data.append(bbc_food_data(), ignore_index=True)
    recipes_data = recipes_data.append(epicurious_data(), ignore_index=True)
    recipes_data = recipes_data.append(chowhound_data(), ignore_index=True)
    recipes_data = recipes_data.append(bbc_good_food_data(), ignore_index=True)
    recipes_data = recipes_data.append(saveur_data(), ignore_index=True)
    # save pandas dataframe in pickle format
    save_obj(recipes_data, "recipes_data")
    # insert cuisine details into MongoDB
    coll.insert_many(recipes_data.to_dict('records'))


if __name__ == '__main__':

    # clean data from all sources and combine into one dataframe \
    # and store the merged data in mongoDB and pickle file
    combine_data()
