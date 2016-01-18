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


def get_content_from_url(link):
    """
    Make web request and collect webpage content
    :param  link (str): web page link
    :return  html content for web page
    """
    # make request with input link and return content of web link

    # sleep time before making web request
    (SCRAPING_REQUEST_STAGGER)
    # make get request of link
    response = requests.get(link)
    # if status code of response is not 200, then return false
    if response.status_code != 200:
        return False
    # return web page html content
    return response.content


def get_number_of_recipes(cuisine):
    """
    Make web request to cuisine url and get number of recipes for cuisine
    :param  cuisine (str): cuisine name to make search request for
    :return  number of recipes (int) or None if no content for url
    """
    # get number of recipes for cuisine

    # create a full link using cuisine_link and cuisine name
    # to obtain web content from link
    cuisine_link = URL + cuisine
    cuisine_recipes = get_content_from_url(cuisine_link)
    # if no content is returned from cuisine link page, return none
    if not cuisine_recipes:
        print "no content for:", cuisine_link
        return None
    # convert web content to soup to better access content
    soup_cuisine = BeautifulSoup(cuisine_recipes)
    # get recipe-count for cuisine
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
    # create link for given cuisine and page number and obtain recipe links from page
    link = CUISINE_URL.format(str(page), cuisine)
    cuisine_recipe_links = get_content_from_url(link)
    # if no content is returned from cuisine search page link, return none
    if not cuisine_recipe_links:
        print "no content for:", link
        return None
    # convert search results page content to beautifulsoup
    soup_search = BeautifulSoup(cuisine_recipe_links)
    # return list of links for cuisine page
    return soup_search.find("div", {"id": "article-list"}).find_all("h3")


def get_recipe(r_link):
    """
    Make web request to recipe page and get the recipe content
    :param  r_link (str): recipe link
    :return  html content for web page in beautifulsoup format
                    or None (if no content)
    """
    # make web request and obtain site content for recipe page
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
    # recipe title
    return soup_recipe.find("h1", {"class": "fn"}).get_text()


def get_recipe_chef(soup_recipe):
    """
    Get recipe chef name from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe chef name or None for no content
    """
    # recipe chef name
    chef_name = soup_recipe.find("span", {"class": "author"})
    # if chef name is not given for recipe, return none
    if not chef_name:
        return None
    # else return chef name
    return chef_name.get_text()


def get_description(soup_recipe):
    """
    Get recipe description from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe description / summary
    """
    # recipe description
    description = soup_recipe.find("span", {"class": "summary"})
    # if description is not given for recipe, return none
    if not description:
        return None
    # else, return recipe descriptipn
    return description.get_text()


def get_recipe_ingredients(soup_recipe):
    """
    Get recipe ingredients from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe ingredient list
    """
    # recipe ingredient list
    ingredients_list = soup_recipe.find_all("p", {"class": "ingredient"})
    ingredients = []
    # append each ingredient to list
    for ing in ingredients_list:
        ingredients.append(ing.get_text())
    # return ingredient list
    return ingredients


def get_recipe_preperation(soup_recipe):
    """
    Get recipe preperation steps from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe preperation steps as a list
    """
    # recipe preperation steps
    prep_steps = soup_recipe.find_all("li", {"class": "instruction"})
    prep = []
    # append each preperation step to list
    for step in prep_steps:
        # get text for each step and strip new line characters at both ends
        prep.append(step.get_text().strip())
    # return preperation steps
    return prep


def get_recipe_time(soup_recipe):
    """
    Get recipe prep and cooking times from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe preperation time and recipe cooking time
                or None if content not available
    """
    # recipe preperation time
    prep_time = soup_recipe.find("span", {"class": "prepTime"})
    # if recipe has prep_time given
    if prep_time:
        prep_time = prep_time.get_text()
    # if recipe has no prep time, set preperation time to none
    else:
        prep_time = None
    # recipe cooking time
    cooking_time = soup_recipe.find("span", {"class": "cookTime"})
    # if recipe has cooking_time given
    if cooking_time:
        cooking_time = cooking_time.get_text()
    # if recipe has no cooking time, set cooking time to none
    else:
        cooking_time = None
    # return preperation time and cooking time
    return prep_time, cooking_time


def get_servings(soup_recipe):
    """
    Get recipe servings/yield from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe servings/yield or None if content not available
    """
    # recipe servings
    servings = soup_recipe.find("h3", {"class": "yield"})
    # if servings are not given for recipe, return none
    if not servings:
        return None
    # else return recipe servings
    return servings.get_text()


def get_recommendations(soup_recipe):
    """
    Get recipe recommendation score from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe recommendation score or None if content not available
    """
    # recipe recommendation score
    recommendations = soup_recipe.find("h2", {"class": "description"})
    # if recommendation score is not given for recipe, return none
    if not recommendations:
        return None
    # else return recipe recommendation score
    return recommendations.get_text()


def get_image_source(soup_recipe):
    """
    Get recipe image source from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe image source or None if content not available
    """
    # recipe image source
    image_source = soup_recipe.find("img", {"id": "food-image"})
    # if image source is not given for recipe, return none
    if not image_source:
        return None
    # else return image source
    return image_source["src"]


def get_recipe_details(recipe_links):
    """
    Get necessary recipe details from all recipe links
    :param  recipe_links (list): recipe links for each cuisine
    :return  recipe details in dictionary format
    """
    # obtain necessary recipe details from recipe page and store in dictionary
    # with (key, value) pairs as (recipe title, corresponding details dictionary)
    cuisine_recipes = {}
    # loop over recipe links to get recipe details for each recipe page
    for r in recipe_links:
        recipe = {}
        # format recipe link
        recipe['r_link'] = r.a["href"]
        print "recipe link: ", recipe['r_link']
        # get recipe html content for recipe link and convert to beautifulsoup format
        soup_recipe = get_recipe(recipe['r_link'])
        # get recipe title
        recipe['recipe title'] = get_recipe_title(soup_recipe)
        # get chef name
        recipe['chef'] = get_recipe_chef(soup_recipe)
        # get recipe description/summary
        recipe['description'] = get_description(soup_recipe)
        # get recipe ingredient list
        recipe['ingredient list'] = get_recipe_ingredients(soup_recipe)
        # get recipe preperation steps list
        recipe['preperation steps'] = get_recipe_preperation(soup_recipe)
        # get recipe preperation time and cooking time
        recipe['prep_time'], recipe['cook_time'] = get_recipe_time(soup_recipe)
        # get recipe servings/yield
        recipe['servings'] = get_servings(soup_recipe)
        # get recipe recommendation score
        recipe['recommendations'] = get_recommendations(soup_recipe)
        # get recipe image source
        recipe['image_source'] = get_image_source(soup_recipe)
        # store recipe details in a dictionary with recipe title as key
        cuisine_recipes[recipe['recipe title']] = recipe
    # return recipe details dictionary for all cuisine recipes
    return cuisine_recipes


def get_recipe_links(cuisine, pages):
    """
    Get recipe details from cuisine search pages
    :params  cuisine (str): cuisine name
             pages (int): number of search result pages for cuisine
    :return  recipe details in dictionary format
    """
    recipe_links = []
    # loop over each page in cuisine to get all recipe details
    for page in xrange(1, pages + 1):
        sleep(SCRAPING_REQUEST_STAGGER)
        # recipe links from each cuisine search page
        recipe_links.extend(get_cuisine_pages(cuisine, page))
    # get recipe details for all recipe links
    cuisine_recipes = get_recipe_details(recipe_links)
    # return dictionary of recipe details
    return cuisine_recipes


def get_cuisine_recipes(cuisines):
    """
    Get recipe details for cuisines, store in mongoDB,
    and convert details dictionary into pandas dataframe
    :param  cuisines (list): cuisines in BBC Food
    :return  recipe details in pandas dataframe
    """

    # to store data in a pandas Dataframe
    cuisine_df = pd.DataFrame()

    # loop over each cuisine and store data for that cuisine recipies
    for cuisine in cuisines:
        cuisine_dict = {}
        cuisine_dict['cuisine'] = cuisine
        cuisine_dict['source'] = 'BBC Food'
        # convert text to lower case and replace all spaces in cuisine title with '_', as used by website
        cuisine_no_space = cuisine.lower().replace(" ", "_")
        # get number of recipes for cuisine
        cuisine_dict['num_recipes'] = get_number_of_recipes(cuisine_no_space)
        # convert number of recipes into number of pages to scrape
        cuisine_dict['pages'] = int(ceil(cuisine_dict['num_recipes'] /
            NUMBER_OF_RECIPES_PER_PAGE))
        # print cuisine details
        print '#####'
        print "Cuisine: %s \t Number of recipes: %d \t\t Number of pages: %d" \
            % (cuisine, cuisine_dict['num_recipes'], cuisine_dict['pages'])
        # get recipe details for all recipes in cuisine
        cuisine_dict['recipes_details'] = get_recipe_links(cuisine_no_space,
            cuisine_dict['pages'])
        # insert cuisine details into MongoDB
        coll.insert_one(cuisine_dict)
        # convert dictionary into a dataframe and append each cuisine details to the dataframe
        cuisine_df = cuisine_df.append(pd.DataFrame.from_dict(cuisine_dict,
            orient='columns'), ignore_index=True)
    # return recipe details detaframe
    return cuisine_df


if __name__ == '__main__':
    # list of cuisines on BBC Food
    cuisines = ['African', 'American', 'British', 'Caribbean', 'Chinese', , 'French',
    'Greek', 'Indian', 'Irish', 'Italian', 'Japanese', 'Mexican', 'Nordic',
    'North African', 'Portuguese', 'South American', 'Spanish', 'Thai and South-east Asian',
    'Turkish and Middle Eastern']
    # get recipe details for all cuisines
    cuisine_dataframe = get_cuisine_recipes(cuisines)
    # save pandas dataframe in pickle format
    save_obj(cuisine_dataframe, "recipes_data_bbc_food")
