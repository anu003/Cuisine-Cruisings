"""
##### Web scrape Chowhound website for recipes (no cuisine labels for these recipes)
##### store recipe details in MongoDB and a pickle file
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
# link for Chowhound recipes
URL = 'http://www.chowhound.com/recipes?page={}'
# number of recipes per page for search results
NUMBER_OF_RECIPES_PER_PAGE = 27


# create MongoDB database and collection
DB_NAME = 'PROJECT_RECIPIES'
COLLECTION_NAME = 'Chowhound'

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
    # make request with the input link and return the content of the web link

    # sleep time before making web request
    sleep(SCRAPING_REQUEST_STAGGER)
    # get request of link
    response = requests.get(link)
    # if the status code of response is not 200, then return false
    if response.status_code != 200:
        return False
    # return web page html content
    return response.content


def get_number_of_pages():
    """
    Make web request to cuisine url and get number of recipes for cuisine
    :return  number of recipes (int) or None if no content for url
    """
    # get number of recipes from the first recipe page

    # create a full link using cuisine_link and cuisine name
    # to obtain web content from link
    first_page_link = URL.format("1")
    cuisine_recipes = get_content_from_url(first_page_link)
    # if no content is returned from the cuisine link page, return none
    if not cuisine_recipes:
        print "no content for:", first_page_link
        return None
    # convert web content to soup to better access content
    soup_cuisine = BeautifulSoup(cuisine_recipes)
    # get recipe-count for website
    # select characters from phrase and convert it into integer
    return int(soup_cuisine.find("span", {"class": "last"}).a["href"].split('=')[1])


def get_recipe_links_by_page(page):
    """
    Get recipe links for search page
    :param  page (int): page number to get recipe links from
    :return  list of recipe links for page
    """
    # create link for given search page number and obtain recipe links from page

    # create a full link using url and page number to obtain web content from link
    page_link = URL.format(page)
    cuisine_recipe_links = get_content_from_url(page_link)
    # if no content is returned from for search page link, return none
    if not cuisine_recipe_links:
        print "no content for:", link
        return None
    # convert search results page content to beautifulsoup
    soup_search = BeautifulSoup(cuisine_recipe_links)
    # return list of links for cuisine page
    return soup_search.find_all("div", {"class": "image_link_medium"})


def get_recipe(recipe_link):
    """
    Make web request to recipe page and get the recipe content
    :param  r_link (str): recipe link
    :return  html content for web page in beautifulsoup format
                    or None (if no content)
    """
    # make web request and obtain site content for recipe page
    recipe_response = get_content_from_url(recipe_link)
    # if no content is returned for recipe link, return none
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
    # recipe title
    return soup_recipe.find("h1", {"itemprop": "name"}).get_text().strip()


def get_recipe_chef(soup_recipe):
    """
    Get recipe chef name from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe chef name or None for no content
    """
    # recipe chef name
    chef_name = soup_recipe.find("span", {"itemprop": "author"})
    # if chef name is not given for recipe
    if not chef_name:
        return None
    # else, strip new line characters on both sides and "By " from front
    return chef_name.get_text().strip()


def get_description(soup_recipe):
    """
    Get recipe description from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe description / summary
    """
    # recipe description
    description = soup_recipe.find("div", {"itemprop": "description"})
    # if description is not given for recipe, return none
    if not description:
        return None
    # else return recipe descriptipn
    return description.get_text().strip()


def get_recipe_ingredients(soup_recipe):
    """
    Get recipe ingredients from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe ingredient list
    """
    # recipe ingredient list
    ingredients_list = soup_recipe.find_all("li", {"itemprop": "ingredients"})
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
    prep_steps = soup_recipe.find("div",
        {"itemprop": "recipeInstructions"}).find_all("li")
    prep = []
    # append each preperation step to list
    for step in prep_steps:
        # get text for the each step and strip of new line characters at both ends
        prep.append(step.get_text().strip())
    # return preperation steps
    return prep


def get_recipe_time(soup_recipe):
    """
    Get recipe total and active times from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe total time and recipe active time
                or None if content not available
    """
    # recipe total time
    total_time = soup_recipe.find("time", {"itemprop": "totalTime"})
    # if recipe has total_time given
    if total_time:
        total_time = total_time.get_text().strip()
    # if recipe has no total time, set total time to none
    else:
        total_time = None
    # recipe active time
    active_time = soup_recipe.find("span", {"class": "frr_totaltime frr_active"})
    # if recipe has active_time given
    if active_time:
        active_time = active_time.find("time").get_text().strip()
    # if recipe has no active time, set active time to none
    else:
        active_time = None
    # return preperation time and cooking time
    return total_time, active_time


def get_servings(soup_recipe):
    """
    Get recipe servings/yield from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe servings/yield or None if content not available
    """
    # recipe servings
    servings = soup_recipe.find("span", {"itemprop": "recipeYield"})
    # if servings are not given for recipe, return none
    if not servings:
        return None
    # else return recipe servings
    return servings.get_text()


def get_recipe_difficulty(soup_recipe):
    """
    Get recipe difficulty level from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe difficulty level or None if content not available
    """
    # recipe difficulty level
    difficulty = soup_recipe.find("span", {"class": "frr_difficulty fr_sep"})
    # if difficulty leve is not given for recipe, return none
    if not difficulty:
        return None
    # else return the recipe difficulty level
    return difficulty.get_text().strip()


def get_ratings(soup_recipe):
    """
    Get recipe ratings and number of ratings from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe rating and number of ratings or None (for both) \
                if content not available
    """
    # recipe ratings
    ratings = soup_recipe.find("span", {"itemprop": "ratingValue"})
    # if recipe has no ratings, set ratings to none
    if not ratings:
        ratings = None
    # else if recipe has ratings
    else:
        ratings = ratings.get_text()
    # recipe number of ratings
    rating_count = soup_recipe.find("span", {"itemprop": "reviewCount"})
    # if recipe has no ratings count, set ratings count to none
    if not rating_count:
        rating_count = None
    # else if recipe has ratings count
    else:
        rating_count = rating_count.get_text()
    # return ratings and ratings count
    return ratings, rating_count


def get_nutrition_per_serving(soup_recipe):
    """
    Get nutritional values per serving for recipe from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  string of (nutrition name, value) or None if content not available
    """
    # recipe nutritional value
    nutritional_info = soup_recipe.find("div", {"class": "nutritional-info"})
    # if nutitionalinfo is not given for recipe, return none
    if not nutritional_info:
        return None
    # else return the nutritional information
    return nutritional_info.get_text()


def get_image_source(soup_recipe):
    """
    Get recipe image source from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe image source or None if content not available
    """
    # recipe image source
    image_source = soup_recipe.find("img", {"id": "recipe_top_img"})
    # if image source is not there for recipe, return none
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
        soup_recipe = BeautifulSoup(r)
        # there are some ads among the recipe links, so get details only for the
        # links that have link contains 'www.chowhound.com'
        # format recipe link
        if "www.chowhound.com" in r.a["href"]:
            recipe = {}
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
            # get recipe total time and active time
            recipe['total_time'], recipe['active_time'] = get_recipe_time(soup_recipe)
            # get recipe servings/yield
            recipe['servings'] = get_servings(soup_recipe)
            # get recipe difficulty/skill level
            recipe['skill_level'] = get_recipe_difficulty(soup_recipe)
            # get recipe recommendation score and number of recommendations
            recipe['rating'], recipe['rating count'] = get_ratings(soup_recipe)
            # get recipe nutrition information
            recipe['nutritional_info'] = get_nutrition_per_serving(soup_recipe)
            # get recipe image source
            recipe['image_source'] = get_image_source(soup_recipe)
            # store recipe details in a dictionary with recipe title as key
            cuisine_recipes[recipe['recipe title']] = recipe
    # return recipe details dictionary for all cuisine recipes
    return cuisine_recipes


def get_recipe_links(pages):
    """
    Get recipe details from recipe search pages
    :params  pages (int): number of search result pages for recipes
    :return  recipe details in dictionary format
    """

    recipe_links = []
    # loop over each page in the cuisine to obtain all the recipe details
    for page in xrange(1, pages+1):
        sleep(SCRAPING_REQUEST_STAGGER)
        # recipe links from each search page
        recipe_links.extend(get_recipe_links_by_page(page))
    # get recipe details for unique recipe links
    cuisine_recipes = get_recipe_details(list(set(recipe_links)))
    # return dictionary of recipe details
    return cuisine_recipes


def get_recipes(num_of_pages):
    """
    Get recipe details for cuisines, store in mongoDB,
    and convert details dictionary into pandas dataframe
    :param  cuisines (list): cuisines in BBC Food
    :return  recipe details in pandas dataframe
    """

    # to store the data in a pandas Dataframe
    recipe_df = pd.DataFrame()
    recipe_dict = {}
    recipe_dict['cuisine'] = 'Unknown'
    recipe_dict['source'] = 'Chowhound'
    # calculate number of recipes for using recipes per page and number of pages
    recipe_dict['num_recipes'] = NUMBER_OF_RECIPES_PER_PAGE * num_of_pages
    # number of pages to scrape
    recipe_dict['pages'] = num_of_pages
    # print the cuisine details
    print '#####'
    print "Cuisine: %s \t Number of recipes: %r \t\t Number of pages: %r" \
        % (recipe_dict['cuisine'], recipe_dict['num_recipes'], recipe_dict['pages'])
    # get recipe links for all recipes in website
    recipe_dict['recipe_links'] = get_recipe_links(recipe_dict['pages'])
    # get recipe details for all recipes links
    recipe_dict['recipes_details'] = get_recipe_links(recipe_dict['pages'])
    # insert cuisine details into MongoDB
    coll.insert_one(recipe_dict)
    # convert the dictionary into a dataframe and append it to the final dataframe
    recipe_df = pd.DataFrame.from_dict(recipe_dict, orient='columns')
    # return recipe details detaframe
    return recipe_df


if __name__ == '__main__':
    # get number of search pages to scrape
    num_of_pages = get_number_of_pages()
    # get recipe details for all recipes
    recipe_dataframe = get_recipes(num_of_pages)
    # save pandas dataframe in pickle format
    save_obj(recipe_dataframe, "recipes_data_chowhound")
