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
    sleep(SCRAPING_REQUEST_STAGGER)
    # get request of link
    response = requests.get(link)
    # if the status code of response is not 200, then return false
    if response.status_code != 200:
        return False
    # return web page html content
    return response.content


def get_number_of_recipes(att_value):
    """
    Make web request to cuisine url and get number of recipes for cuisine
    :param  att_value (int): attribute value corresponding to a cuisine for
                            which search request is to be made
    :return  number of recipes (int) or None if no content for url
    """
    # get number of recipes for cuisine

    # create a full link using cuisine_link and cuisine name
    # to obtain web content from link
    cuisine_link = CUISINE_URL.format(att_value)
    cuisine_recipes = get_content_from_url(cuisine_link)
    # if no content is returned from the cuisine link page, return none
    if not cuisine_recipes:
        print "no content for:", cuisine_link
        return None
    # convert web content to soup to better access the content
    soup_cuisine = BeautifulSoup(cuisine_recipes)
    # get recipe-count for cuisine
    # select characters from phrase and convert it into integer
    return int(soup_cuisine.find("div", {"id": "sr_sortby"}).
        find("p").get_text().split()[2])


def get_cuisine_pages(att_value, page):
    """
    Make web request to cuisine search page and collect recipe links for page
    :params  att_value (str): attribute value corresponding to a cuisine for
                            which search request is to be made
             page (int): search results page number from which content needed
                        to be colleceted
    :return  list of recipe links for search page url or None (if no content)
    """
    # create link for given cuisine and page number and obtain recipe links from page

    # if page is 1, use cuisine_url and att_value to make get request
    if page == 1:
        link = CUISINE_URL.format(att_value)
    # else, use cuisine_recipes_url with att_value and page to make get request
    else:
        link = CUISINE_RECIPES_URL.format(att_value, page,
            int(NUMBER_OF_RECIPES_PER_PAGE[0] +
                (page-2)*NUMBER_OF_RECIPES_PER_PAGE[1] + 1))
    cuisine_recipe_links = get_content_from_url(link)
    # if no content is returned from cuisine recipe page link, return none
    if not cuisine_recipe_links:
        print "no content for:", link
        return None
    # else, convert recipe results page content to beautifulsoup
    soup_search = BeautifulSoup(cuisine_recipe_links)
    # return the list of links for the cuisine page
    return soup_search.find("div", {"id": "recipe_main"}).find_all("a",
        {"class": "recipeLnk"})


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
        print "no content for:", recipe_link
        return None
    # else, return webpage content in beautifulsoup format
    return BeautifulSoup(recipe_response)


def get_recipe_title(soup_recipe):
    """
    Get recipe title from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe title
    """
    # get recipe title and strip spaces and new line characters from the ends
    return soup_recipe.find("h1", {"itemprop": "name"}).get_text().strip()


def get_recipe_chef(soup_recipe):
    """
    Get recipe chef name from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe chef name or None for no content
    """
    # recipe chef name
    chef_name = soup_recipe.find("span", {"itemprop": "author"})
    # if chef name is not given for recipe, return none
    if not chef_name:
        return None
    # else, strip new line characters on both sides and the "By " from front
    return chef_name.get_text().strip()[3:]


def get_description(soup_recipe):
    """
    Get recipe description from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe description / summary
    """
    # recipe description
    summary = soup_recipe.find("div", {"itemprop": "description"})
    # if description is not given for recipe, return none
    if not summary:
        return None
    # else, return recipe descriptipn
    return summary.find("p").get_text().strip()


def get_recipe_ingredients(soup_recipe):
    """
    Get recipe ingredients from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe ingredient list
    """
    # recipe ingredient list
    ingredients_list = soup_recipe.find_all("li", {"class": "ingredient"})
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
    prep_steps = soup_recipe.find_all("li", {"class": "preparation-step"})
    prep = []
    # append each preperation step to list
    for step in prep_steps:
        # get text for the each step and strip of new line characters at both ends
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
    prep_time = soup_recipe.find("p", {"class": "recipe-metadata__prep-time"})
    # if recipe has prep_time given, set prep_time equal to the prep-time value
    if prep_time:
        prep_time = prep_time.get_text()
    # if recipe has no prep time, set preperation time to none
    else:
        prep_time = None
    # recipe cooking time
    cooking_time = soup_recipe.find("p", {"class": "recipe-metadata__cook-time"})
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
    servings = soup_recipe.find("dd", {"itemprop": "recipeYield"})
    # if servings are not given for recipe, return none
    if not servings:
        return None
    # else return recipe servings
    return servings.get_text()


def get_recommendations(soup_recipe):
    """
    Get recipe ratings score and number of recommendations from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe ratings score and the number of recommendations \
                 or None if content not available
    """
    # recipe ratings score
    ratings = soup_recipe.find("span", {"class": "rating"})
    # if ratings score is not there for recipe, set ratings score to none
    if not ratings:
        ratings = None
    # else get recipe ratings score
    else:
        ratings = ratings.get_text()
    recommendations = soup_recipe.find("div", {"class": "prepare-again-rating"})
    # if recommendations are not there for recipe, set recommendations to none
    if not recommendations:
        recommendations = None
    # else get recipe number of recommendations
    else:
        recommendations = recommendations.find("span").get_text()
    # return recipe ratings score and number of recommendations
    return ratings, recommendations


def get_nutrition_per_serving(soup_recipe):
    """
    Get nutritional values per serving for recipe from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  nutrition information in string format or None if content not available
    """
    # recipe nutrition per serving
    nutritional_info = soup_recipe.find("div", {"class": "nutritional-info"})
    # if nutrition information is not given for recipe, return none
    if not nutritional_info:
        return None
    #  return nutrition information in string format
    return nutritional_info.get_text()


def get_image_source(soup_recipe):
    """
    Get recipe image source from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe image source or None if content not available
    """
    # recipe image source
    image_source = soup_recipe.find("div", {"class": "recipe-image"})
    # if image source is not given for recipe, return none
    if not image_source:
        return None
    # else return image source
    return image_source.find("img")["src"]


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
        recipe_link = r["href"]
        print "recipe link: ", recipe_link
        # get recipe html content for recipe link and convert to beautifulsoup format
        soup_recipe = get_recipe(recipe_link)
        # if link has content
        if soup_recipe:
            recipe['r_link'] = recipe_link
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
            # get recipe ratings score and number of recommendations
            recipe['rating'], recipe['recommendation'] = get_recommendations(soup_recipe)
            # get recipe nutrition information
            recipe['nutritional_info'] = get_nutrition_per_serving(soup_recipe)
            # get recipe image source
            recipe['image_source'] = get_image_source(soup_recipe)
        # store recipe details in a dictionary with recipe title as key
        cuisine_recipes[recipe['recipe title']] = recipe
    # return recipe details dictionary for all cuisine recipes
    return cuisine_recipes


def get_recipe_links(att_value, pages):
    """
    Get recipe details from cuisine search pages
    :params  att_value (int): attribute value for cuisine (unique for each cuisine)
             pages (int): number of search result pages for cuisine
    :return  recipe details for cuisine in dictionary format
    """
    # loop over each page for the cuisine to obtain all recipe details
    recipe_links = []
    for page in xrange(1, pages + 1):
        sleep(SCRAPING_REQUEST_STAGGER)
        # recipe links from each cuisine search page
        recipe_links.extend(get_cuisine_pages(att_value, page))
    # get recipe details for all recipe links
    cuisine_recipes = get_recipe_details(recipe_links)
    # return dictionary of recipe details
    return cuisine_recipes


def get_cuisine_recipes(cuisines, att_values):
    """
    Get recipe details for cuisines, store in mongoDB,
    and convert details dictionary into pandas dataframe
    :params  cuisines (list): cuisines under Epicurious search
             att_values (list): corresponding attribute values for the cuisines
    :return  recipe details in pandas dataframe
    """

    # to store the data in a pandas Dataframe
    cuisine_df = pd.DataFrame()
    # loop over each cuisine and store data regarding that cuisine recipies
    for cuisine, att_value in zip(cuisines, att_values):
        cuisine_dict = {}
        cuisine_dict['cuisine'] = cuisine
        cuisine_dict['source'] = 'Epicurious'
        # obtain the number of recipes for each cuisine
        cuisine_dict['num_recipes'] = get_number_of_recipes(att_value)
        # convert number of recipes into pages to scrape
        # 20 search results for first search page and 30 each for the remaining
        if cuisine_dict['num_recipes'] <= 20:
            cuisine_dict['pages'] = int(ceil(cuisine_dict['num_recipes'] /
                NUMBER_OF_RECIPES_PER_PAGE[0]))
        else:
            cuisine_dict['pages'] = int(1 + ceil((cuisine_dict['num_recipes'] -
                NUMBER_OF_RECIPES_PER_PAGE[0]) / NUMBER_OF_RECIPES_PER_PAGE[1]))
        # print the cuisine details
        print '#####'
        print "Cuisine: %s \t Number of recipes: %r \t\t Number of pages: %r" % \
            (cuisine, cuisine_dict['num_recipes'], cuisine_dict['pages'])
        # get all recipe details for for each cuisine
        cuisine_dict['recipes_details'] = get_recipe_links(att_value,
            cuisine_dict['pages'])
        # insert cuisine details into MongoDB
        coll.insert_one(cuisine_dict)
        # convert the dictionary into a dataframe and append it to the final dataframe
        cuisine_df = cuisine_df.append(pd.DataFrame.from_dict(cuisine_dict,
            orient='columns'), ignore_index=True)
    # return recipe details detaframe
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
    # get recipe details for all cuisines
    cuisine_dataframe = get_cuisine_recipes(cuisines, att_values)
    # save pandas dataframe in pickle format
    save_obj(cuisine_dataframe, "recipes_data_epicurious")
