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


def get_number_of_pages():
    """
    Make web request to cuisine url and get number of recipes for cuisine
    :return  number of recipes (int) or None if no content for url
    """
    first_page_link = URL.format("1")
    cuisine_recipes = get_content_from_url(first_page_link)
    if not cuisine_recipes:
        print "no content for:", first_page_link
        return None
    soup_cuisine = BeautifulSoup(cuisine_recipes)
    # select characters from phrase and convert it into integer
    return int(soup_cuisine.find("span", {"class": "last"}).a["href"].split('=')[1])


def get_recipe_links_by_page(page):
    """
    Get recipe links for search page
    :param  page (int): page number to get recipe links from
    :return  list of recipe links for page
    """
    page_link = URL.format(page)
    cuisine_recipe_links = get_content_from_url(page_link)
    if not cuisine_recipe_links:
        print "no content for:", link
        return None
    soup_search = BeautifulSoup(cuisine_recipe_links)
    return soup_search.find_all("div", {"class": "image_link_medium"})


def get_recipe(recipe_link):
    """
    Make web request to recipe page and get the recipe content
    :param  r_link (str): recipe link
    :return  html content for web page in beautifulsoup format
                    or None (if no content)
    """
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
    return chef_name.get_text().strip()


def get_description(soup_recipe):
    """
    Get recipe description from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe description / summary
    """
    description = soup_recipe.find("div", {"itemprop": "description"})
    if not description:
        return None
    return description.get_text().strip()


def get_recipe_ingredients(soup_recipe):
    """
    Get recipe ingredients from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe ingredient list
    """
    ingredients_list = soup_recipe.find_all("li", {"itemprop": "ingredients"})
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
    prep_steps = soup_recipe.find("div",
        {"itemprop": "recipeInstructions"}).find_all("li")
    prep = []
    for step in prep_steps:
        prep.append(step.get_text().strip())
    return prep


def get_recipe_time(soup_recipe):
    """
    Get recipe total and active times from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe total time and recipe active time
                or None if content not available
    """
    total_time = soup_recipe.find("time", {"itemprop": "totalTime"})
    if total_time:
        total_time = total_time.get_text().strip()
    else:
        total_time = None
    active_time = soup_recipe.find("span", {"class": "frr_totaltime frr_active"})
    if active_time:
        active_time = active_time.find("time").get_text().strip()
    else:
        active_time = None
    return total_time, active_time


def get_servings(soup_recipe):
    """
    Get recipe servings/yield from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe servings/yield or None if content not available
    """
    servings = soup_recipe.find("span", {"itemprop": "recipeYield"})
    if not servings:
        return None
    return servings.get_text()


def get_recipe_difficulty(soup_recipe):
    """
    Get recipe difficulty level from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe difficulty level or None if content not available
    """
    difficulty = soup_recipe.find("span", {"class": "frr_difficulty fr_sep"})
    if not difficulty:
        return None
    return difficulty.get_text().strip()


def get_ratings(soup_recipe):
    """
    Get recipe ratings and number of ratings from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe rating and number of ratings or None (for both) \
                if content not available
    """
    ratings = soup_recipe.find("span", {"itemprop": "ratingValue"})
    if not ratings:
        ratings = None
    else:
        ratings = ratings.get_text()
    rating_count = soup_recipe.find("span", {"itemprop": "reviewCount"})
    if not rating_count:
        rating_count = None
    else:
        rating_count = rating_count.get_text()
    return ratings, rating_count


def get_nutrition_per_serving(soup_recipe):
    """
    Get nutritional values per serving for recipe from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  string of (nutrition name, value) or None if content not available
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
    image_source = soup_recipe.find("img", {"id": "recipe_top_img"})
    if not image_source:
        return None
    return image_source["src"]


def get_recipe_details(recipe_links):
    """
    Get necessary recipe details from all recipe links and store in dictionary \
    with (key, value) pairs as (recipe title, corresponding details dictionary)
    there are some ads among the recipe links, so get details only for the \
    links that have link contains 'www.chowhound.com'
    :param  recipe_links (list): recipe links for each cuisine
    :return  recipe details in dictionary format
    """
    cuisine_recipes = {}
    for r in recipe_links:
        soup_recipe = BeautifulSoup(r)
        if "www.chowhound.com" in r.a["href"]:
            recipe = {}
            recipe['r_link'] = r.a["href"]
            print "recipe link: ", recipe['r_link']
            soup_recipe = get_recipe(recipe['r_link'])
            recipe['recipe title'] = get_recipe_title(soup_recipe)
            recipe['chef'] = get_recipe_chef(soup_recipe)
            recipe['description'] = get_description(soup_recipe)
            recipe['ingredient list'] = get_recipe_ingredients(soup_recipe)
            recipe['preperation steps'] = get_recipe_preperation(soup_recipe)
            recipe['total_time'], recipe['active_time'] = get_recipe_time(soup_recipe)
            recipe['servings'] = get_servings(soup_recipe)
            recipe['skill_level'] = get_recipe_difficulty(soup_recipe)
            recipe['rating'], recipe['rating count'] = get_ratings(soup_recipe)
            recipe['nutritional_info'] = get_nutrition_per_serving(soup_recipe)
            recipe['image_source'] = get_image_source(soup_recipe)
            cuisine_recipes[recipe['recipe title']] = recipe
    return cuisine_recipes


def get_recipe_links(pages):
    """
    Get recipe details from recipe search pages
    :params  pages (int): number of search result pages for recipes
    :return  recipe details in dictionary format
    """
    recipe_links = []
    for page in xrange(1, pages+1):
        sleep(SCRAPING_REQUEST_STAGGER)
        recipe_links.extend(get_recipe_links_by_page(page))
    cuisine_recipes = get_recipe_details(list(set(recipe_links)))
    return cuisine_recipes


def get_recipes(num_of_pages):
    """
    Get recipe details for cuisines, store in mongoDB,
    and convert details dictionary into pandas dataframe
    :param  cuisines (list): cuisines in BBC Food
    :return  recipe details in pandas dataframe
    """

    recipe_df = pd.DataFrame()
    recipe_dict = {}
    recipe_dict['cuisine'] = 'Unknown'
    recipe_dict['source'] = 'Chowhound'
    recipe_dict['num_recipes'] = NUMBER_OF_RECIPES_PER_PAGE * num_of_pages
    recipe_dict['pages'] = num_of_pages
    print '#####'
    print "Cuisine: %s \t Number of recipes: %r \t\t Number of pages: %r" \
        % (recipe_dict['cuisine'], recipe_dict['num_recipes'], recipe_dict['pages'])
    recipe_dict['recipe_links'] = get_recipe_links(recipe_dict['pages'])
    recipe_dict['recipes_details'] = get_recipe_links(recipe_dict['pages'])
    coll.insert_one(recipe_dict)
    recipe_df = pd.DataFrame.from_dict(recipe_dict, orient='columns')
    return recipe_df


if __name__ == '__main__':
    num_of_pages = get_number_of_pages()
    recipe_dataframe = get_recipes(num_of_pages)
    save_obj(recipe_dataframe, "recipes_data_chowhound")
