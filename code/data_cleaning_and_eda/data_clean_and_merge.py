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
    with open('../../data/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    """
    Load object from pickel file in data folder
    :param  name (str): file-name to load object from
    :return  object in original format
    """
    with open('../../data/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def replace_all(text):
    """
    Replace all html encoded content in the data with their resspective ascii \
    encoded values (alphabets and symbols)
    Also remove any brackets from the data ('[]{}()')
    :param  text (str): text from recipe details dictionary in database
    :return  replaced ascii encodable text content in string format
    """
    vulgar_fraction_puctuation = non_ascii_elements()
    for old_value, new_value in vulgar_fraction_puctuation.iteritems():
        text = text.replace(old_value, new_value)
    return text


def convert_fractions_and_remove_brackets(data):
    """
    Convert all non-ascii occurences in recipe details dictionary
    :param  data (dictionary): dict of recipe details for one recipe
    :return  dictionary with all the non-ascii replaced with their \
                correspinding ascii values
    """
    for key_value in data:
        if type(data[key_value]) == list:
            new_list = []
            for list_row in data[key_value]:
                new_list.append(replace_all(list_row))
            data[key_value] = new_list
        if type(data[key_value]) == unicode:
            data[key_value] = replace_all(data[key_value])
    return data


def bbc_food_data():
    """
    Load bbc food data, replace non-ascii chars with their correspinding ascii \
    values and remove duplicates
    :param  none
    :return  pandas dataframe with all the non-ascii replaced and duplicates removed
    """
    bbc_data = load_obj('recipes_data_bbc_food').sort_index()
    # remove float indices
    bbc_data.reset_index(inplace=True)
    bbc_data.drop('index', axis=1, inplace=True)
    bbc_data['recipes_details'] = map(convert_fractions_and_remove_brackets,
        bbc_data['recipes_details'])
    bbc_data['recipe_title'] = map(lambda x: x['recipe title'],
        bbc_data['recipes_details'])
    bbc_data['recipe_link'] = map(lambda x: x['r_link'], bbc_data['recipes_details'])
    bbc_data.drop_duplicates(['recipe_link', 'cuisine'], keep='first', inplace=True)
    bbc_data.reset_index(inplace=True)
    bbc_data.drop(['index', 'recipe_link'], axis=1, inplace=True)
    return bbc_data


def epicurious_data():
    """
    Load epicurious data, replace non-ascii chars with their correspinding ascii \
    values and remove duplicates
    :param  none
    :return  pandas dataframe with all the non-ascii replaced and duplicates removed
    """
    epicurious_data = load_obj('recipes_data_epicurious').sort_index()
    # remove float indices
    epicurious_data.reset_index(inplace=True)
    epicurious_data.drop('index', axis=1, inplace=True)
    epicurious_data['recipes_details'] = map(convert_fractions_and_remove_brackets,
        epicurious_data['recipes_details'])
    epicurious_data['recipe_title'] = map(lambda x: x['recipe title'],
        epicurious_data['recipes_details'])
    epicurious_data['recipe_link'] = map(lambda x: x['r_link'],
        epicurious_data['recipes_details'])
    epicurious_data.drop_duplicates(['recipe_link', 'cuisine'],
        keep='first', inplace=True)
    epicurious_data.reset_index(inplace=True)
    epicurious_data.drop(['index', 'recipe_link'], axis=1, inplace=True)
    return epicurious_data


def chowhound_data():
    """
    Load chowhound data, replace non-ascii chars with their correspinding ascii \
    values and remove duplicates
    :param  none
    :return  pandas dataframe with all the non-ascii replaced and duplicates removed
    """
    chowhound_data = load_obj('recipes_data_chowhound').sort_index()
    chowhound_data.reset_index(inplace=True)
    chowhound_data.drop('index', axis=1, inplace=True)
    chowhound_data['recipes_details'] = map(convert_fractions_and_remove_brackets,
        chowhound_data['recipes_details'])
    chowhound_data['recipe_title'] = map(lambda x: x['recipe title'],
        chowhound_data['recipes_details'])
    chowhound_data['recipe_link'] = map(lambda x: x['r_link'],
        chowhound_data['recipes_details'])
    chowhound_data.drop_duplicates(['recipe_link', 'cuisine'], keep='first',
        inplace=True)
    chowhound_data.reset_index(inplace=True)
    chowhound_data.drop(['index', 'recipe_link'], axis=1, inplace=True)
    return chowhound_data


def bbc_good_food_data():
    """
    Load bbc good food data, replace non-ascii chars with their correspinding ascii \
    values and remove duplicates
    :param  none
    :return  pandas dataframe with all the non-ascii replaced and duplicates removed
    """
    bbc_good_food_data = load_obj('recipes_data_bbc_good_food').sort_index()
    # remove float indices
    bbc_good_food_data.reset_index(inplace=True)
    bbc_good_food_data.drop('index', axis=1, inplace=True)
    bbc_good_food_data['recipes_details'] = map(convert_fractions_and_remove_brackets,
        bbc_good_food_data['recipes_details'])
    bbc_good_food_data['recipe_title'] = map(lambda x: x['recipe title'],
        bbc_good_food_data['recipes_details'])
    bbc_good_food_data['recipe_link'] = map(lambda x: x['r_link'],
        bbc_good_food_data['recipes_details'])
    bbc_good_food_data.drop_duplicates(['recipe_link', 'cuisine'],
        keep='first', inplace=True)
    bbc_good_food_data.reset_index(inplace=True)
    bbc_good_food_data.drop(['index', 'recipe_link'], axis=1, inplace=True)
    return bbc_good_food_data


def saveur_data():
    """
    Load saveur data, replace non-ascii chars with their correspinding ascii \
    values and remove duplicates
    :param  none
    :return  pandas dataframe with all the non-ascii replaced and duplicates removed
    """
    saveur_data = load_obj('recipes_data_saveur').sort_index()
    saveur_data.reset_index(inplace=True)
    saveur_data.drop('index', axis=1, inplace=True)
    saveur_data['recipes_details'] = map(convert_fractions_and_remove_brackets,
        saveur_data['recipes_details'])
    saveur_data['recipe_title'] = map(lambda x: x['recipe title'],
        saveur_data['recipes_details'])
    saveur_data['recipe_link'] = map(lambda x: x['r_link'],
        saveur_data['recipes_details'])
    saveur_data.drop_duplicates(['recipe_link', 'cuisine'], keep='first', inplace=True)
    saveur_data.reset_index(inplace=True)
    saveur_data.drop(['index', 'recipe_link'], axis=1, inplace=True)
    return saveur_data


def combine_data():
    """
    Clean data from all sources, merge the data to form a new pandas dataframe \
    and store the merged data in mongoDB and pickle file
    :param  none
    :return  none
    """
    recipes_data = pd.DataFrame()
    recipes_data = recipes_data.append(bbc_food_data(), ignore_index=True)
    recipes_data = recipes_data.append(epicurious_data(), ignore_index=True)
    recipes_data = recipes_data.append(chowhound_data(), ignore_index=True)
    recipes_data = recipes_data.append(bbc_good_food_data(), ignore_index=True)
    recipes_data = recipes_data.append(saveur_data(), ignore_index=True)
    save_obj(recipes_data, "recipes_data")
    coll.insert_many(recipes_data.to_dict('records'))


if __name__ == '__main__':

    combine_data()
