"""
##### Web scrape Epicurious website for recipes by cuisine
##### store recipe details for all cuisines in MongoDB and a pickle file
"""

from time import sleep
import requests
from bs4 import BeautifulSoup
from math import ceil
import pandas as pd
from pymongo import MongoClient
import pickle


# sleep time between web requests (in seconds)
SCRAPING_REQUEST_STAGGER = 5.0
# link for Epicurious cuisine recipes
CUISINE_URL = 'http://www.epicurious.com/tools/searchresults?type=simple&att={}'
# link for Epicurious cuisine recipes for pages 2 and higher
CUISINE_RECIPES_URL = 'http://www.epicurious.com/tools/searchresults?att={}&type=simple&pageNumber={}&pageSize=30&resultOffset={}'
# link for Epicurious recipes
RECIPE_URL = 'http://www.epicurious.com{}'
# first page has 20 recipes and all other pages have 30 each
NUMBER_OF_RECIPES_PER_PAGE = [20., 30.]


# create MongoDB database and collection
DB_NAME = 'PROJECT_RECIPIES'
COLLECTION_NAME = 'EPICUR'

# connect to mongodb to store scraped data
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


def get_content_from_url(link):
    """
    Make web request and collect webpage content
    :param  link (str): web page link
    :return  html content for web page
    """
    # sleep time before making web request
    sleep(SCRAPING_REQUEST_STAGGER)
    response = requests.get(link)
    if response.status_code != 200:
        return False
    return response.content


def get_number_of_recipes(att_value):
    """
    Make web request to cuisine url and get number of recipes for cuisine
    :param  att_value (int): attribute value corresponding to a cuisine for
                            which search request is to be made
    :return  number of recipes (int) or None if no content for url
    """
    cuisine_link = CUISINE_URL.format(att_value)
    cuisine_recipes = get_content_from_url(cuisine_link)
    if not cuisine_recipes:
        print "no content for:", cuisine_link
        return None
    soup_cuisine = BeautifulSoup(cuisine_recipes)
    # select characters from phrase and convert it into integer
    return int(soup_cuisine.find("div", {"id": "sr_sortby"}).
        find("p").get_text().split()[2])


def get_cuisine_pages(att_value, page):
    """
    Make web request to cuisine search page and collect recipe links for page
    For page 1, use cuisine_url and att_value to make get request, for all other \
    pages, use cuisine_recipes_url with att_value and page to make get request
    :params  att_value (str): attribute value corresponding to a cuisine for
                            which search request is to be made
             page (int): search results page number from which content needed
                        to be colleceted
    :return  list of recipe links for search page url or None (if no content)
    """
    if page == 1:
        link = CUISINE_URL.format(att_value)
    else:
        link = CUISINE_RECIPES_URL.format(att_value, page,
            int(NUMBER_OF_RECIPES_PER_PAGE[0] +
                (page-2)*NUMBER_OF_RECIPES_PER_PAGE[1] + 1))
    cuisine_recipe_links = get_content_from_url(link)
    if not cuisine_recipe_links:
        print "no content for:", link
        return None
    soup_search = BeautifulSoup(cuisine_recipe_links)
    return soup_search.find("div", {"id": "recipe_main"}).find_all("a",
        {"class": "recipeLnk"})


def get_recipe(r_link):
    """
    Make web request to recipe page and get the recipe content
    :param  r_link (str): recipe link
    :return  html content for web page in beautifulsoup format
                    or None (if no content)
    """
    recipe_link = RECIPE_URL.format(r_link)
    recipe_response = get_content_from_url(recipe_link)
    if not recipe_response:
        print "no content for:", recipe_link
        return None
    return BeautifulSoup(recipe_response)


def get_recipe_title(soup_recipe):
    """
    Get recipe title from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe title
    """
    return soup_recipe.find("h1", {"itemprop": "name"}).get_text().strip()


def get_recipe_chef(soup_recipe):
    """
    Get recipe chef name from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe chef name or None for no content
    """
    chef_name = soup_recipe.find("span", {"itemprop": "author"})
    if not chef_name:
        return None
    return chef_name.get_text().strip()[3:]


def get_description(soup_recipe):
    """
    Get recipe description from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe description / summary
    """
    summary = soup_recipe.find("div", {"itemprop": "description"})
    if not summary:
        return None
    return summary.find("p").get_text().strip()


def get_recipe_ingredients(soup_recipe):
    """
    Get recipe ingredients from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe ingredient list
    """
    ingredients_list = soup_recipe.find_all("li", {"class": "ingredient"})
    ingredients = []
    for ing in ingredients_list:
        ingredients.append(ing.get_text())
    return ingredients


def get_recipe_preperation(soup_recipe):
    """
    Get recipe preperation steps from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe preperation steps as a list
    """
    prep_steps = soup_recipe.find_all("li", {"class": "preparation-step"})
    prep = []
    for step in prep_steps:
        prep.append(step.get_text().strip())
    return prep


def get_recipe_time(soup_recipe):
    """
    Get recipe prep and cooking times from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe preperation time and recipe cooking time
                or None if content not available
    """
    prep_time = soup_recipe.find("p", {"class": "recipe-metadata__prep-time"})
    if prep_time:
        prep_time = prep_time.get_text()
    else:
        prep_time = None
    cooking_time = soup_recipe.find("p", {"class": "recipe-metadata__cook-time"})
    if cooking_time:
        cooking_time = cooking_time.get_text()
    else:
        cooking_time = None
    return prep_time, cooking_time


def get_servings(soup_recipe):
    """
    Get recipe servings/yield from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe servings/yield or None if content not available
    """
    servings = soup_recipe.find("dd", {"itemprop": "recipeYield"})
    if not servings:
        return None
    return servings.get_text()


def get_recommendations(soup_recipe):
    """
    Get recipe ratings score and number of recommendations from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe ratings score and the number of recommendations \
                 or None if content not available
    """
    ratings = soup_recipe.find("span", {"class": "rating"})
    if not ratings:
        ratings = None
    else:
        ratings = ratings.get_text()
    recommendations = soup_recipe.find("div", {"class": "prepare-again-rating"})
    if not recommendations:
        recommendations = None
    else:
        recommendations = recommendations.find("span").get_text()
    return ratings, recommendations


def get_nutrition_per_serving(soup_recipe):
    """
    Get nutritional values per serving for recipe from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  nutrition information in string format or None if content not available
    """
    nutritional_info = soup_recipe.find("div", {"class": "nutritional-info"})
    if not nutritional_info:
        return None
    return nutritional_info.get_text()


def get_image_source(soup_recipe):
    """
    Get recipe image source from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe image source or None if content not available
    """
    image_source = soup_recipe.find("div", {"class": "recipe-image"})
    if not image_source:
        return None
    return image_source.find("img")["src"]


def get_recipe_details(recipe_links):
    """
    Get necessary recipe details from all recipe links and store in dictionary \
    with (key, value) pairs as (recipe title, corresponding details dictionary)
    :param  recipe_links (list): recipe links for each cuisine
    :return  recipe details in dictionary format
    """
    cuisine_recipes = {}
    for r in recipe_links:
        recipe = {}
        recipe_link = r["href"]
        print "recipe link: ", recipe_link
        soup_recipe = get_recipe(recipe_link)
        if soup_recipe:
            recipe['r_link'] = recipe_link
            recipe['recipe title'] = get_recipe_title(soup_recipe)
            recipe['chef'] = get_recipe_chef(soup_recipe)
            recipe['description'] = get_description(soup_recipe)
            recipe['ingredient list'] = get_recipe_ingredients(soup_recipe)
            recipe['preperation steps'] = get_recipe_preperation(soup_recipe)
            recipe['prep_time'], recipe['cook_time'] = get_recipe_time(soup_recipe)
            recipe['servings'] = get_servings(soup_recipe)
            recipe['rating'], recipe['recommendation'] = get_recommendations(soup_recipe)
            recipe['nutritional_info'] = get_nutrition_per_serving(soup_recipe)
            recipe['image_source'] = get_image_source(soup_recipe)
        cuisine_recipes[recipe['recipe title']] = recipe
    return cuisine_recipes


def get_recipe_links(att_value, pages):
    """
    Get recipe details from cuisine search pages
    :params  att_value (int): attribute value for cuisine (unique for each cuisine)
             pages (int): number of search result pages for cuisine
    :return  recipe details for cuisine in dictionary format
    """
    recipe_links = []
    for page in xrange(1, pages + 1):
        sleep(SCRAPING_REQUEST_STAGGER)
        recipe_links.extend(get_cuisine_pages(att_value, page))
    cuisine_recipes = get_recipe_details(recipe_links)
    return cuisine_recipes


def get_cuisine_recipes(cuisines, att_values):
    """
    Get recipe details for cuisines, store in mongoDB,
    and convert details dictionary into pandas dataframe
    There are 20 search results for first search page and 30 each for the remaining
    :params  cuisines (list): cuisines under Epicurious search
             att_values (list): corresponding attribute values for the cuisines
    :return  recipe details in pandas dataframe
    """
    cuisine_df = pd.DataFrame()
    for cuisine, att_value in zip(cuisines, att_values):
        cuisine_dict = {}
        cuisine_dict['cuisine'] = cuisine
        cuisine_dict['source'] = 'Epicurious'
        cuisine_dict['num_recipes'] = get_number_of_recipes(att_value)
        if cuisine_dict['num_recipes'] <= 20:
            cuisine_dict['pages'] = int(ceil(cuisine_dict['num_recipes'] /
                NUMBER_OF_RECIPES_PER_PAGE[0]))
        else:
            cuisine_dict['pages'] = int(1 + ceil((cuisine_dict['num_recipes'] -
                NUMBER_OF_RECIPES_PER_PAGE[0]) / NUMBER_OF_RECIPES_PER_PAGE[1]))
        print '#####'
        print "Cuisine: %s \t Number of recipes: %r \t\t Number of pages: %r" % \
            (cuisine, cuisine_dict['num_recipes'], cuisine_dict['pages'])
        cuisine_dict['recipes_details'] = get_recipe_links(att_value,
            cuisine_dict['pages'])
        coll.insert_one(cuisine_dict)
        cuisine_df = cuisine_df.append(pd.DataFrame.from_dict(cuisine_dict,
            orient='columns'), ignore_index=True)
    return cuisine_df


if __name__ == '__main__':

    # dictionary of cuisines on Epicurious with their corresponding attribute values
    cuisine_att_values = {'African': 1, 'Argentine': 329, 'Asian': 3, 'British': 315,
    'Cajun/Creole': 4, 'Californian': 334, 'Central American/Caribbean': 5,
    'Central/South American': 6, 'Chinese': 7, 'Cuban': 326,
    'Eastern European/Russian': 8, 'European': 314, 'German': 11, 'Greek': 12,
    'Indian': 13, 'Irish': 14, 'Israeli': 323, 'Italian': 15, 'Jewish': 17,
    'Korean': 309, 'Latin American': 325, 'Mediterranean': 18, 'Mexican': 19,
    'Middle Eastern': 20, 'Moroccan': 21, 'New England': 335, 'Northern Italian': 318,
    'Nuevo Latino': 327, 'Scandinavian': 22, 'South American': 328,
    'Southeast Asian': 310, 'Southern': 338, 'Southwestern': 23,
    'Spanish/Portuguese': 24, 'Thai': 25, 'Tex-Mex': 339, 'Turkish': 331, 'Vietnamese': 26}
    cuisines = cuisine_att_values.keys()
    att_values = cuisine_att_values.values()
    cuisine_dataframe = get_cuisine_recipes(cuisines, att_values)
    save_obj(cuisine_dataframe, "recipes_data_epicurious")
