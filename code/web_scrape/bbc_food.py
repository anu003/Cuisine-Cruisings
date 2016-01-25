"""
##### Web scrape BBC Food website for recipes by cuisine
##### store recipe details for all cuisines in MongoDB and a pickle file
"""

from time import sleep
import requests
from bs4 import BeautifulSoup
import re
from math import ceil
import pandas as pd
from pymongo import MongoClient
import pickle


# sleep time between web requests (in seconds)
SCRAPING_REQUEST_STAGGER = 5.0
# main url for BBC food cuisine collections page
URL = 'http://www.bbc.co.uk/food/cuisines/'
# cuisine search url
CUISINE_URL = 'http://www.bbc.co.uk/food/recipes/search?page={}&cuisines%5B0%5D={}&sortBy=lastModified'
# recipe url
RECIPE_URL = 'http://www.bbc.co.uk{}'
# number of recipes per page for search results
NUMBER_OF_RECIPES_PER_PAGE = 15.


# create MongoDB database and collection
DB_NAME = 'PROJECT_RECIPIES'
COLLECTION_NAME = 'BBC'

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
    (SCRAPING_REQUEST_STAGGER)
    response = requests.get(link)
    if response.status_code != 200:
        return False
    return response.content


def get_number_of_recipes(cuisine):
    """
    Make web request to cuisine url and get number of recipes for cuisine
    :param  cuisine (str): cuisine name to make search request for
    :return  number of recipes (int) or None if no content for url
    """
    cuisine_link = URL + cuisine
    cuisine_recipes = get_content_from_url(cuisine_link)
    if not cuisine_recipes:
        print "no content for:", cuisine_link
        return None
    soup_cuisine = BeautifulSoup(cuisine_recipes)
    # remove non-alphanumeric characters from recipe-count and convert it into integer
    return int(re.sub('\W', '', soup_cuisine.find("span",
        {"class": "recipe-count"}).get_text()))


def get_cuisine_pages(cuisine, page):
    """
    Make web request to cuisine search page and collect recipe links for page
    :params  cuisine (str): cuisine name to make search request for
             page (int): page number of search results to collect content from
    :return  list of recipe links for search page url or None (if no content)
    """
    link = CUISINE_URL.format(str(page), cuisine)
    cuisine_recipe_links = get_content_from_url(link)
    if not cuisine_recipe_links:
        print "no content for:", link
        return None
    soup_search = BeautifulSoup(cuisine_recipe_links)
    return soup_search.find("div", {"id": "article-list"}).find_all("h3")


def get_recipe(r_link):
    """
    Make web request to recipe page and get the recipe content
    :param  r_link (str): recipe link
    :return  html content for web page in beautifulsoup format
                    or None (if no content)
    """
    recipe_link = RECIPE_URL.format(r_link)
    recipe_response = get_content_from_url(recipe_link)
    # if no content is returned from cuisine search page link, return none
    if not recipe_response:
        print "no content for: ", recipe_link
        return None
    # else, return webpage content in beautifulsoup format
    return BeautifulSoup(recipe_response)


def get_recipe_title(soup_recipe):
    """
    Get recipe title from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe title
    """
    return soup_recipe.find("h1", {"class": "fn"}).get_text()


def get_recipe_chef(soup_recipe):
    """
    Get recipe chef name from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe chef name or None for no content
    """
    chef_name = soup_recipe.find("span", {"class": "author"})
    if not chef_name:
        return None
    return chef_name.get_text()


def get_description(soup_recipe):
    """
    Get recipe description from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe description / summary
    """
    description = soup_recipe.find("span", {"class": "summary"})
    if not description:
        return None
    return description.get_text()


def get_recipe_ingredients(soup_recipe):
    """
    Get recipe ingredients from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe ingredient list
    """
    ingredients_list = soup_recipe.find_all("p", {"class": "ingredient"})
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
    prep_steps = soup_recipe.find_all("li", {"class": "instruction"})
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
    prep_time = soup_recipe.find("span", {"class": "prepTime"})
    if prep_time:
        prep_time = prep_time.get_text()
    else:
        prep_time = None
    cooking_time = soup_recipe.find("span", {"class": "cookTime"})
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
    servings = soup_recipe.find("h3", {"class": "yield"})
    if not servings:
        return None
    return servings.get_text()


def get_recommendations(soup_recipe):
    """
    Get recipe recommendation score from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe recommendation score or None if content not available
    """
    recommendations = soup_recipe.find("h2", {"class": "description"})
    if not recommendations:
        return None
    return recommendations.get_text()


def get_image_source(soup_recipe):
    """
    Get recipe image source from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe image source or None if content not available
    """
    image_source = soup_recipe.find("img", {"id": "food-image"})
    if not image_source:
        return None
    return image_source["src"]


def get_recipe_details(recipe_links):
    """
    Get necessary recipe details from all recipe links and store in dictionary
    with (key, value) pairs as (recipe title, corresponding details dictionary)
    :param  recipe_links (list): recipe links for each cuisine
    :return  recipe details in dictionary format
    """
    cuisine_recipes = {}
    for r in recipe_links:
        recipe = {}
        recipe['r_link'] = r.a["href"]
        print "recipe link: ", recipe['r_link']
        soup_recipe = get_recipe(recipe['r_link'])
        recipe['recipe title'] = get_recipe_title(soup_recipe)
        recipe['chef'] = get_recipe_chef(soup_recipe)
        recipe['description'] = get_description(soup_recipe)
        recipe['ingredient list'] = get_recipe_ingredients(soup_recipe)
        recipe['preperation steps'] = get_recipe_preperation(soup_recipe)
        recipe['prep_time'], recipe['cook_time'] = get_recipe_time(soup_recipe)
        recipe['servings'] = get_servings(soup_recipe)
        recipe['recommendations'] = get_recommendations(soup_recipe)
        recipe['image_source'] = get_image_source(soup_recipe)
        cuisine_recipes[recipe['recipe title']] = recipe
    return cuisine_recipes


def get_recipe_links(cuisine, pages):
    """
    Get recipe details from cuisine search pages
    :params  cuisine (str): cuisine name
             pages (int): number of search result pages for cuisine
    :return  recipe details in dictionary format
    """
    recipe_links = []
    for page in xrange(1, pages + 1):
        sleep(SCRAPING_REQUEST_STAGGER)
        recipe_links.extend(get_cuisine_pages(cuisine, page))
    cuisine_recipes = get_recipe_details(recipe_links)
    return cuisine_recipes


def get_cuisine_recipes(cuisines):
    """
    Get recipe details for cuisines, store in mongoDB,
    and convert details dictionary into pandas dataframe
    :param  cuisines (list): cuisines in BBC Food
    :return  recipe details in pandas dataframe
    """
    cuisine_df = pd.DataFrame()
    for cuisine in cuisines:
        cuisine_dict = {}
        cuisine_dict['cuisine'] = cuisine
        cuisine_dict['source'] = 'BBC Food'
        cuisine_no_space = cuisine.lower().replace(" ", "_")
        cuisine_dict['num_recipes'] = get_number_of_recipes(cuisine_no_space)
        cuisine_dict['pages'] = int(ceil(cuisine_dict['num_recipes'] /
            NUMBER_OF_RECIPES_PER_PAGE))
        print '#####'
        print "Cuisine: %s \t Number of recipes: %d \t\t Number of pages: %d" \
            % (cuisine, cuisine_dict['num_recipes'], cuisine_dict['pages'])
        cuisine_dict['recipes_details'] = get_recipe_links(cuisine_no_space,
            cuisine_dict['pages'])
        coll.insert_one(cuisine_dict)
        cuisine_df = cuisine_df.append(pd.DataFrame.from_dict(cuisine_dict,
            orient='columns'), ignore_index=True)
    return cuisine_df


if __name__ == '__main__':
    # list of cuisines on BBC Food
    cuisines = ['African', 'American', 'British', 'Caribbean', 'Chinese', , 'French',
    'Greek', 'Indian', 'Irish', 'Italian', 'Japanese', 'Mexican', 'Nordic',
    'North African', 'Portuguese', 'South American', 'Spanish', 'Thai and South-east Asian',
    'Turkish and Middle Eastern']
    cuisine_dataframe = get_cuisine_recipes(cuisines)
    save_obj(cuisine_dataframe, "recipes_data_bbc_food")
