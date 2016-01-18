"""
##### Load cleaned & merged recipe data and find recipe ingredients for all
##### recipes
"""

import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from non_ascii_elements_and_stop_words import recipe_stop_words_cooking
from non_ascii_elements_and_stop_words import recipe_stop_words_processing
from non_ascii_elements_and_stop_words import recipe_stop_words_sizes
from non_ascii_elements_and_stop_words import recipe_stop_words_other

# create MongoDB database and collection
DB_NAME = 'PROJECT_RECIPES'
COLLECTION_NAME = 'RECIPES_DATA_WITH_INGREDIENTS'

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


def lemmatize_text(word):
    """
    Lemmatize input word using WordNet Lemmatizer
    :param  word (str): word to be lemmatized using word
    :return  lemmatized word in string format
    """

    # define the lemmatizer model
    wordnet_lemmatizer = WordNetLemmatizer()
    # return the lemmatized word
    return wordnet_lemmatizer.lemmatize(word)


def stop_words_lemmatized():
    """
    Lemmatize each wor in the combined set of stopwords
    :param  none
    :return  set of lemmatized stop words
    """

    # combine all sets of stop word into one set
    set_of_stop_words = recipe_stop_words_cooking() | \
        recipe_stop_words_processing() | recipe_stop_words_sizes() | \
        recipe_stop_words_other()
    # lemmatize each word in the set of stopwords after removing '-' \
    # from each word
    stop_words_lematized = map(lambda x: lemmatize_text
        (x.replace('-', '')), set_of_stop_words)
    # number of stop words
    stopwords_count = len(stop_words_lematized)
    # return set of lemmatized stop words
    return stop_words_lematized


def word_tokenize_ingredients(ingredient_list_per_recipe):
    """
    Tokenize ingredient list for one recipe using nltk tagging
    :params  ingredient_list_per_recipe (list): ingredient line items \
                for one recipe
    :return  list of word and word_tag tuples in ingredient line items
    """

    # map each line item in the ingredient list to a list of word and \
    # word_tag tuples
    return map(lambda x: nltk.pos_tag(word_tokenize(x), tagset='universal'),
        ingredient_list_per_recipe)


def word_exists_in_set(item):
    """
    Checks if the word is a stop word or not (both nltk stopwords as well \
        as the pre-defined stop-words), returns true if item is in stop-words
    else returns false
    :param  item (str): word from ingredient line items
    :return  boolean, true if a version of item is in stop-words, else false
    """

    # lemmatize lower-case word
    item = lemmatize_text(item.lower())
    # lematized set of pre-defined stop-words
    lemmatized_stop_words = set(stop_words_lemmatized())
    # for each unique word in combined stop-words set, checks if ingredient\
    # item starts with a stop word
    for each_set in [set(stopwords.words('english')), lemmatized_stop_words]:
        # if lower-case ingredient item (with both '-' and '.' removed) \
        # is in either of the stop-word sets, then return true
        if item.lower().replace('-', '').replace('.', '') in each_set:
            return True
        # else, loop over all lemmatized stop-words, to check if a stop-word \
        # stars with the ingredient item
        for word in lemmatized_stop_words:
            # if a stop-word starts with ingredient item, then return true
            if word.startswith(item):
                return True
    # if both the above conditions are not true then return false to indicate \
    # that the ingredient item is not a stop-word
    return False


def ingredient_words_per_line(ingredient_line):
    """
    For every word in the ingredient line, check if word is a possible \
    ingredient word, based on corresponding word_tag and the word itself \
    being in stop-words set
    :param  ingredient_line (list of tuples): one line from recipe \
                ingredient list with word and word_tag tuples
    :return  list of words from ingredient line to be considered as \
                ingredients or none to indicate a stop-word or alpha-numeric char
    """

    ingredient_word_list = []
    # loop over each word in the ingredient line to determine if word is a \
    # possible ingredient or a stop-word/alpha-numeric char
    for ingredient_word in ingredient_line:
        # lemmatize lower-case ingredient word after replacing '/' with a space
        ingredient_word_lemmatized = lemmatize_text(ingredient_word[0].
            replace('/', ' ').lower())
        # if word_tag is not a number, other, conjunction, adposition, punctuation \
        # or particle, is not alpha-numeric and is not stop-word then append the
        # word to the possible ingredient word list
        if ingredient_word[1] not in ['NUM', 'X', 'CONJ', 'ADP', '.', 'PRT']:
            # if word is alpha-numeric, then it is not an ingredient word
            if ingredient_word_lemmatized.replace('-', '').isalpha():
                # any version of word should not be in stop-words list append
                # word ot the ingredient list
                if not word_exists_in_set(ingredient_word_lemmatized):
                    ingredient_word_list.append(ingredient_word_lemmatized)
                # else, if word is stop-word and the current ingredient list has
                # some elements and if the previous element in list is not 'none',
                # then append 'none' to the ingredient list
                elif (len(ingredient_word_list) > 0) &
                (ingredient_word_list[-1:] != ['none']):
                    ingredient_word_list.append('none')
        # if the word_tag is number, other, conjunction, adposition, punctuation \
        # or particle, ingredient_word_list has atleast one element and previous \
        # element in list is not 'none', then append 'none' to the ingredient list
        elif (len(ingredient_word_list) > 0) &
        (ingredient_word_list[-1:] != ['none']):
            ingredient_word_list.append('none')
    # return ingredient list with possible ingredients and 'none' to represent one \
    # or more stop-words/alpha-numeric char/word_tags indicating not ingredient
    return ingredient_word_list


def ingredients_per_line(ingredient_word_list):
    """
    Get ingredients for each line in the ingredient list for the recipe after \
    joining n-grams (words are considered n-grams if there is no 'none' seperating \
    n-consecutive words)
    :param  ingredient_word_list (list): words from one line in ingredient list \
                to be considered as ingredients
    :return  ingredients for line in ingredient list, after joining n-grams
    """

    ingredients_list_per_line = []
    ingredients_to_be_joined = []
    # for each item in the ingredient word list, if the item is not 'none', \
    # add word to either of these lists: ingredients_to_be_joined or ingredientlist
    for ing_pos, ing_value in enumerate(ingredient_word_list):
        if ing_value != 'none':
            # if there are no words to be joined, and this is the last item in \
            # ingredient word list or next item in ingredient list is 'none', \
            # add item to ingredient list
            # else add item to ingredients to be joind list
            if len(ingredients_to_be_joined) == 0:
                if ing_pos == (len(ingredient_word_list) - 1):
                    ingredients_list_per_line.append(ing_value)
                elif ingredient_word_list[ing_pos+1] == 'none':
                    ingredients_list_per_line.append(ing_value)
                else:
                    ingredients_to_be_joined.append(ing_value)
            # else if ingredient is the last item in the list, add to ingredients \
            # to be joined, join the items as one multi-word ingredient and add to \
            # ingredients list, else add ingredient to the list of word to be joined
            else:
                if ing_pos == (len(ingredient_word_list) - 1):
                    ingredients_to_be_joined.append(ing_value)
                    joined_ingredient = " ".join(ingredients_to_be_joined)
                    ingredients_list_per_line.append(joined_ingredient)
                else:
                    ingredients_to_be_joined.append(ing_value)
        # if item is 'none' and there are elements to be joined, join elements in \
        # ingredients_to_be_joined and add the joined ingredient to ingredient list
        else:
            if len(ingredients_to_be_joined) > 0:
                joined_ingredient = " ".join(ingredients_to_be_joined)
                ingredients_list_per_line.append(joined_ingredient)
                ingredients_to_be_joined = []
    # return a list of ingredients for one line in ingredient list for recipe
    return ingredients_list_per_line


def recipe_ingredient_list_generator(ingredient_list_per_recipe):
    """
    Get ingredients for all lines in ingredient list for recipe after joining \
    n-grams (words are considered n-grams if there is no 'none' seperating \
    n-consecutive words)
    :param  ingredient_list_per_recipe (list): ingredient line items (string) for \
                one recipe
    :return  list of unique ingredients for recipe
    """

    # tokenize the words in each list item
    ingredient_list_per_recipe = word_tokenize_ingredients(ingredient_list_per_recipe)
    recipe_ingredient_list = []
    # loop over each line in ingredient list and generate list of ingredinets for recipe
    for ingredient_line in ingredient_list_per_recipe:
        # get list of words in ingredients line to be considered as ingredients
        ingredient_word_list_per_line = ingredient_words_per_line(ingredient_line)
        # get ingredients for line in ingredients line, after joining n-grams
        ingredients_list_per_line = ingredients_per_line(ingredient_word_list_per_line)
        # add all ingredient n-grams to a list of ingredients for recipe
        recipe_ingredient_list.extend(ingredients_list_per_line)
    # return unique ingredient items for recipe
    return list(set(recipe_ingredient_list))


def ingredient_data():
    """
    Load cleaned and merged data in pandas dataframe, get ingredients for all \
    recipes, insert ingredients into dataframe \
    store final dataframe in MondoDB and pickle file
    :param  none
    :return  none
    """

    # load data (which was in pandas format before pickeling) from pickle and sort index
    recipes_data = load_obj("recipes_data").sort_index()
    # get 'ingredient list' from recipes_detilas dictionary and insert a column in \
    # dataframe
    recipes_data['ingredient_list'] = map(lambda x: x['ingredient list'],
        recipes_data['recipes_details'])
    # get 'recipe_ingredients' for each recipe with n-grams and insert a column in \
    # dataframe
    recipes_data['recipe_ingredients'] = map(recipe_ingredient_list_generator,
        recipes_data['ingredient_list'])
    # save pandas dataframe in pickle format
    save_obj(recipes_data, "recipes_data_ingredients")
    # insert recipes data with ingredients into MongoDB
    coll.insert_many(recipes_data.to_dict('records'))
    return


if __name__ == '__main__':

    ingredient_data()
