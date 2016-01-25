"""
##### Load cleaned & merged recipe data and find recipe ingredients for all
##### recipes
"""

import pandas as pd
import pickle
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


def lemmatize_text(word):
    """
    Lemmatize input word using WordNet Lemmatizer
    :param  word (str): word to be lemmatized using word
    :return  lemmatized word in string format
    """
    wordnet_lemmatizer = WordNetLemmatizer()
    return wordnet_lemmatizer.lemmatize(word)


def stop_words_lemmatized():
    """
    Lemmatize each word in the combined set of stopwords
    :param  none
    :return  set of lemmatized stop words
    """
    set_of_stop_words = recipe_stop_words_cooking() | \
        recipe_stop_words_processing() | recipe_stop_words_sizes() | \
        recipe_stop_words_other()
    stop_words_lematized = map(lambda x: lemmatize_text
        (x.replace('-', '')), set_of_stop_words)
    stopwords_count = len(stop_words_lematized)
    return stop_words_lematized


def word_tokenize_ingredients(ingredient_list_per_recipe):
    """
    Tokenize ingredient list for one recipe using nltk tagging
    :params  ingredient_list_per_recipe (list): ingredient line items \
                for one recipe
    :return  list of word and word_tag tuples in ingredient line items
    """
    return map(lambda x: nltk.pos_tag(word_tokenize(x), tagset='universal'),
        ingredient_list_per_recipe)


def word_in_stopwords(item):
    """
    Checks if the lower-case lemmatized word is a stop word or not (both \
    nltk stopwords as well as the pre-defined stop-words), returns true \
    if item is in stop-words else returns false
    :param  item (str): word from ingredient line items
    :return  boolean, true if a version of item is in stop-words, else false
    """

    item = lemmatize_text(item.lower())
    lemmatized_stop_words = set(stop_words_lemmatized())
    for each_set in [set(stopwords.words('english')), lemmatized_stop_words]:
        if item.lower().replace('-', '').replace('.', '') in each_set:
            return True
        for word in lemmatized_stop_words:
            if word.startswith(item):
                return True
    return False


def ingredient_words_per_line(ingredient_line):
    """
    For every word in the ingredient line, check if lower-case lemmatized \
    word is a possible ingredient word, based on corresponding word_tag \
    and the word itself being in the set of stop-words or has \
    alpha-numeric char. Do not consider words with following word-tags,
    [number, other, conjunction, adposition, punctuation, particle].
    :param  ingredient_line (list of tuples): one line from recipe \
                ingredient list with word and word_tag tuples
    :return  list of words from ingredient line to be considered as \
                ingredients or none to indicate a stop-word or alpha-numeric char
    """

    ingredient_word_list = []
    for ingredient_word in ingredient_line:
        ingredient_word_lemmatized = lemmatize_text(ingredient_word[0].
            replace('/', ' ').lower())
        if ingredient_word[1] not in ['NUM', 'X', 'CONJ', 'ADP', '.', 'PRT']:
            if ingredient_word_lemmatized.replace('-', '').isalpha():
                if not word_in_stopwords(ingredient_word_lemmatized):
                    ingredient_word_list.append(ingredient_word_lemmatized)
                elif (len(ingredient_word_list) > 0) & \
                (ingredient_word_list[-1:] != ['none']):
                    ingredient_word_list.append('none')
        elif (len(ingredient_word_list) > 0) & \
        (ingredient_word_list[-1:] != ['none']):
            ingredient_word_list.append('none')
    return ingredient_word_list


def ingredients_per_line(ingredient_word_list):
    """
    Get ingredients for each line in the ingredient list for the recipe after \
    joining n-grams (words are considered n-grams if there is no 'none' seperating \
    n-consecutive words)
    If n-consecutive words are not stop-words, then they are considered \
    n-gram ingredients
    :param  ingredient_word_list (list): words from one line in ingredient list \
                to be considered as ingredients
    :return  ingredients for line in ingredient list, after joining n-grams
    """

    ingredients_list_per_line = []
    ingredients_to_be_joined = []
    for ing_pos, ing_value in enumerate(ingredient_word_list):
        if ing_value != 'none':
            if len(ingredients_to_be_joined) == 0:
                if ing_pos == (len(ingredient_word_list) - 1):
                    ingredients_list_per_line.append(ing_value)
                elif ingredient_word_list[ing_pos+1] == 'none':
                    ingredients_list_per_line.append(ing_value)
                else:
                    ingredients_to_be_joined.append(ing_value)
            else:
                if ing_pos == (len(ingredient_word_list) - 1):
                    ingredients_to_be_joined.append(ing_value)
                    joined_ingredient = " ".join(ingredients_to_be_joined)
                    ingredients_list_per_line.append(joined_ingredient)
                else:
                    ingredients_to_be_joined.append(ing_value)
        else:
            if len(ingredients_to_be_joined) > 0:
                joined_ingredient = " ".join(ingredients_to_be_joined)
                ingredients_list_per_line.append(joined_ingredient)
                ingredients_to_be_joined = []
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

    ingredient_list_per_recipe = word_tokenize_ingredients(ingredient_list_per_recipe)
    recipe_ingredient_list = []
    for ingredient_line in ingredient_list_per_recipe:
        ingredient_word_list_per_line = ingredient_words_per_line(ingredient_line)
        ingredients_list_per_line = ingredients_per_line(ingredient_word_list_per_line)
        recipe_ingredient_list.extend(ingredients_list_per_line)
    return list(set(recipe_ingredient_list))


def ingredient_data():
    """
    Load cleaned and merged data in pandas dataframe, get ingredients for all \
    recipes, insert ingredients into dataframe, remove recipes with no ingredients \
    store final dataframe in MondoDB and pickle file
    :param  none
    :return  none
    """

    recipes_data = load_obj("recipes_data").sort_index()
    recipes_data['ingredient_list'] = map(lambda x: x['ingredient list'],
        recipes_data['recipes_details'])
    print "recipes_data_ing_list"
    recipes_data['recipe_ingredients'] = map(recipe_ingredient_list_generator,
        recipes_data['ingredient_list'])
    print "recipes_data_ing"
    indices_with_no_ing = recipes_data[recipes_data['ingredient_list']\
    .astype(str) == '[]'].index
    recipes_data = recipes_data.drop(recipes_data.index[indices_with_no_ing])
    recipes_data.reset_index(inplace=True)
    recipes_data.drop('index', axis=1, inplace=True)
    save_obj(recipes_data, "recipes_data_ingredients")
    coll.insert_many(recipes_data.to_dict('records'))
    return


if __name__ == '__main__':

    ingredient_data()
