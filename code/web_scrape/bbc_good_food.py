"""
##### Web scrape BBC Good Food website for recipes by cuisine
##### using both static and dynamic webscraping techniques
##### store recipe details for all cuisines in MongoDB and a pickle file
"""

from time import sleep
import time
from math import ceil
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from pymongo import MongoClient
import pickle


# sleep time between web requests (in seconds)
SCRAPING_REQUEST_STAGGER = 5.0
# main search link for BBC Good Food cuisines
SEARCH_URL = 'http://www.bbcgoodfood.com/search/recipes?query=#page={}&path=cuisine/{}'
# link for BBC Good Food cuisine collection
COLLECTION_URL = 'http://www.bbcgoodfood.com/recipes/collection/{}'
# recipe url
RECIPE_URL = 'http://www.bbcgoodfood.com{}'
# number of recipes per page for search results
NUMBER_OF_RECIPES_PER_SEARCH_PAGE = 15.


# create MongoDB database and collection
DB_NAME = 'PROJECT_RECIPIES'
COLLECTION_NAME = 'BBC_GOOD_FOOD'

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


def get_content_from_static_url(link):
    """
    Make web request to static url and collect webpage content
    :param  link (str): web page link
    :return  html content for web page
    """
    # make request with static input link and return content of web link

    # sleep time before making web request
    sleep(SCRAPING_REQUEST_STAGGER)
    # header details for web request
    headers = {"User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, \
        like Gecko) Chrome/47.0.2526.80 Safari/537.36"}
    # make get request of link with the above header details
    response = requests.get(link, headers=headers)
    # if status code of response is not 200, then return false
    if response.status_code != 200:
        return False
    # return web page html content
    return response.content


def get_content_from_dynamic_url(link):
    """
    Make web request to dynamic webpage url and collect webpage content
    :param  link (str): web page link
    :return  html content for web page
    """
    # make web request using Selenium chrome browser driver
    browser = webdriver.Chrome("/Applications/chromedriver")
    # required content loads in about 10 seconds
    # as a buffer set the page load timeout to 25 seconds
    browser.set_page_load_timeout(25)
    # try to load page
    try:
        browser.get(link)
    # if the page load timeout exception is raised, return content of page
    # (this will include required content since that loads in about 10 seconds)
    except:
        page_source = browser.page_source
        browser.quit()
        return page_source
    page_source = browser.page_source
    # quit browser
    browser.quit()
    return page_source


def get_number_of_search_recipes(cuisine):
    """
    Make web request to cuisine url and get the number of search recipes for cuisine
    :param  cuisine (str): cuisine name to make search request for
    :return  number of recipes for cuisine (int) or None (if no content for url)
    """
    # get number of recipe search results for cuisine

    # create a full link using the page number and cuisine name
    # to obtain web content from link
    cuisine_search_link = SEARCH_URL.format(0, cuisine)
    cuisine_recipes = get_content_from_dynamic_url(cuisine_search_link)
    # if no content is returned from the cuisine search link page, return none
    if not cuisine_recipes:
        print "no content for:", cuisine_search_link
        return None
    # convert web content to soup to better access the content
    soup_cuisine = BeautifulSoup(cuisine_recipes)
    # for the given number of recipes per page, calculate number of search result pages for cuisine
    # get recipe-count and convert it into integer
    return int(soup_cuisine.find("h1", {"class": "search-title"}).find("em").get_text())


def get_cuisine_search_pages(cuisine, page):
    """
    Make web request to cuisine search page and collect recipe links for page
    :params  cuisine (str): cuisine name to make search request for
             page (int): page number of search results to collect content from
    :return  list of recipe links for search page url or None (if no content)
    """
    # create link for given cuisine and search page number and obtain recipe links from page
    link = SEARCH_URL.format(page, cuisine)
    cuisine_recipe_links = get_content_from_dynamic_url(link)
    # if no content is returned from cuisine search link page, return none
    if not cuisine_recipe_links:
        print "no content for:", link
        return None
    # convert web content to beautifulsoup format to better access content
    soup_search = BeautifulSoup(cuisine_recipe_links)
    # return the list of links for the cuisine search page
    return soup_search.find_all("h2", {"class": "node-title"})


def get_cuisine_collection_page(cuisine):
    """
    Make web request to cuisine collection page and collect recipe links for first page
    :param  cuisine (str): cuisine name to make search request for
    :return  list of recipe links for colelction first page url or None (if no content)
    """
    # create collection link for given cuisine and obtain recipe links from the page

    # create a full link using the cuisine name to obtain web content from link
    cuisine_link = COLLECTION_URL.format(cuisine)
    cuisine_recipes = get_content_from_static_url(cuisine_link)
    # if no content is returned from the cuisine link page, return none
    if not cuisine_recipes:
        print "no content for:", cuisine_link
        return None
    # convert web content to soup to better access the content
    soup_cuisine = BeautifulSoup(cuisine_recipes)
    # return the list of links for the cuisine collection page
    return soup_cuisine.find_all("h2", {"class": "node-title"})


def get_recipe(r_link):
    """
    Make web request to recipe page and get the recipe content
    :param  r_link (str): recipe link
    :return  html content for the web page in beautifulsoup format
                    or None (if no content)
    """
    # make web request and obtain site content for recipe page
    recipe_link = RECIPE_URL.format(r_link)
    recipe_response = get_content_from_static_url(recipe_link)
    # if no content is returned from cuisine search page link, return none
    if not recipe_response:
        print "no content for: ", recipe_link
        return None
    return BeautifulSoup(recipe_response)


def get_recipe_title(soup_recipe):
    """
    Get recipe title from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe title
    """
    # recipe title
    return soup_recipe.find("h1", {"itemprop": "name"}).get_text()


def get_recipe_chef(soup_recipe):
    """
    Get recipe chef name from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe chef name or None for no content
    """
    # recipe chef name
    chef_name = soup_recipe.find("div",
        {"class": "recipe-header__chef recipe-header__chef--first"}).find("a")
    # if chef name is not given for the recipe, get submitter name
    if not chef_name:
        chef_name = soup_recipe.find("div",
            {"class": "recipe-header__chef recipe-header__chef--first"}).find("span")
    # if submitter name is also not given for the recipe, return none
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
    description = soup_recipe.find("div", {"itemprop": "description"}).find("div",
        {"class": "field-items"}).find("div")
    # if description is not given for recipe, return none
    if not description:
        return None
    # else return recipe descriptipn
    return description.get_text()


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
        ingredients.append(ing.get_text().split('\n')[0])
    # return ingredient list
    return ingredients


def get_recipe_preperation(soup_recipe):
    """
    Get recipe preperation steps from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe preperation steps as a list
    """
    # recipe preperation steps
    prep_steps = soup_recipe.find_all("li", {"itemprop": "recipeInstructions"})
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
    prep_time_check = soup_recipe.find("span", {"class": "recipe-details__cooking-time-prep"})
    # default for prep_time and cooking_time is None, which will be updated if there is a value \
    # for the recipe
    prep_time, cooking_time = None, None
    # if recipe has prep_time given
    if prep_time_check:
        prep_time = prep_time_check.get_text().split(":")[1].strip()
    # recipe cooking time
    cooking_time_check = soup_recipe.find("span", {"class": "recipe-details__cooking-time-cook"})
    # if recipe has cooking_time given
    if cooking_time_check:
        cooking_time = cooking_time_check.get_text().split(":")[1].strip()
    # return preperation time and cooking time
    return prep_time, cooking_time


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
    return servings.get_text().strip()


def get_skill_level(soup_recipe):
    """
    Get recipe skill level from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe skill level or None if content not available
    """
    # recipe skill level
    skill_level = soup_recipe.find("section",
        {"class": "recipe-details__item recipe-details__item--skill-level"}).find("span",
        {"class": "recipe-details__text"})
    # if skill level is not given for recipe, return none
    if not skill_level:
        return None
    # else return recipe skill level
    return skill_level.get_text().strip()


def get_recommendations(soup_recipe):
    """
    Get recipe recommendation score and number of recommendations from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe recommendation score and number of recommendations \
                or None if content not available
    """
    # recipe recommendation score
    ratings = soup_recipe.find("meta", {"itemprop": "ratingValue"})["content"]
    # recipe number of recommendations
    ratings_count = soup_recipe.find("meta", {"itemprop": "ratingCount"})["content"]
    # if recommendation score is not given for recipe, return none for both score and count
    if ratings == 0:
        return None, None
    # else return recipe ratings score and number of recommendations
    return ratings, ratings_count


def get_nutrition_per_serving(soup_recipe):
    """
    Get nutritional values per serving for recipe from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  dictionary of (nutrition name, value) as (key, value) pairs \
                or None if content not available
    """
    # recipe nutrition information
    nutritional_info = soup_recipe.find_all("span", {"class": "nutrition__value"})
    # if nutrition information is not given for recipe, return none
    if not nutritional_info:
        return None
    # else, create a diictionary with nutrition name and the corresponding \
    # nutritional value
    nutrition_name, nutrition_value = [], []
    for nutrition in nutritional_info:
        # get text for each nutrition category
        if nutrition.get_text() != '-':
            nutrition_name.append(nutrition["itemprop"])
            nutrition_value.append(nutrition.get_text())
    # return dictionary of nutritional information
    return dict(zip(nutrition_name, nutrition_value))


def get_image_source(soup_recipe):
    """
    Get recipe image source from recipe content
    :param  soup_recipe (str): recipe content in beautifulsoup format
    :return  recipe image source or None if content not available
    """
    # recipe image source
    image_source = soup_recipe.find("img", {"itemprop": "image"})
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
        recipe_link = r.a["href"]
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
            # get recipe skill level
            recipe['skill_level'] = get_skill_level(soup_recipe)
            # get recipe ratings score and number of ratings
            recipe['rating'], recipe['rating count'] = get_recommendations(soup_recipe)
            # get recipe nutrition information
            recipe['nutritional_info'] = get_nutrition_per_serving(soup_recipe)
            # get recipe image source
            recipe['image_source'] = get_image_source(soup_recipe)
            # store recipe details in a dictionary with recipe title as key
            cuisine_recipes[recipe['recipe title']] = recipe
    # return recipe details dictionary for all cuisine recipes
    return cuisine_recipes


def get_recipe_links(cuisine, pages, collection):
    """
    Get recipe details from cuisine search pages \
    and cuisine colections first page (if cuisine has a collection)
    :params  cuisine (str): cuisine name
             pages (int): number of search result pages for cuisine
             collection (boolean): True if cuisine has collection, else False
    :return  recipe details in dictionary format
    """
    # loop over each page for the cuisine to obtain all recipe details
    recipe_links = []
    for page in xrange(0, pages):
        sleep(SCRAPING_REQUEST_STAGGER)
        # recipe links from each cuisine search page
        recipe_links.extend(get_cuisine_search_pages(cuisine, page))
    # if cuisine is a collection, add unique recipe links from the collection page to the list
    if collection:
        recipe_links.extend(get_cuisine_collection_page(cuisine))
    # get recipe details for all unique recipe links
    cuisine_recipes = get_recipe_details(list(set(recipe_links)))
    # return dictionary of recipe details
    return cuisine_recipes


def get_cuisine_recipes(search_cuisisnes, cuisines):
    """
    Get recipe details for cuisines, store in mongoDB,
    and convert details dictionary into pandas dataframe
    :params  search_cuisines (list): cuisines under BBC Good Food search
             cuisines (list): cuisines under BBC Good Food collections
    :return  recipe details in pandas dataframe
    """

    # to store the data in a pandas Dataframe
    cuisine_df = pd.DataFrame()
    # loop over each cuisine and store data for that cuisine recipies
    for cuisine in search_cuisisnes:
        cuisine_dict = {}
        cuisine_dict['cuisine'] = cuisine
        cuisine_dict['source'] = 'BBC Good Food'
        # convert text to lower case and convert spaces and '&' to '-', as used by website
        cuisine_no_space = cuisine.lower().replace(' & ', '-').replace(' ', '-')
        # get number of recipe search results for each cuisine
        recipes_cuisine_search = get_number_of_search_recipes(cuisine_no_space)
        # convert number of recipes into pages to scrape
        # which will be number search pages and one page for cuisine collection \
        # (if there is collection)
        cuisine_dict['pages'] = int(ceil(recipes_cuisine_search /
            NUMBER_OF_RECIPES_PER_SEARCH_PAGE))
        # default value for collection is false, to indicate that the cuisine is not \
        # in the collection
        collection = False
        # if cuisine is in collections get the links from there as well, and change \
        # collection to true
        if cuisine in cuisines:
            cuisine_dict['pages'] += 1
            collection = True
        cuisine_dict['recipes_details'] = get_recipe_links(cuisine_no_space,
            cuisine_dict['pages']-1, collection)
        # total number of recipes for cuisine is the number of unique recipes in search \
        # combined with collection
        cuisine_dict['num_recipes'] = len(cuisine_dict['recipes_links'])
        # print cuisine details
        print '#####'
        print "Cuisine: %s \t Number of recipes: %d \t\t Number of pages: %d" \
            % (cuisine, cuisine_dict['num_recipes'], cuisine_dict['pages'])
        # insert cuisine details into MongoDB
        coll.insert_one(cuisine_dict)
        # convert dictionary into a dataframe and append each cuisine details to dataframe
        cuisine_df = cuisine_df.append(pd.DataFrame.from_dict(cuisine_dict, orient='columns'),
            ignore_index=True)
    # return recipe details detaframe
    return cuisine_df


if __name__ == '__main__':

    # list of cuisines under BBC Good Food collections
    cuisines = ['American', 'British', 'Caribbean', 'Chinese', 'French', 'Greek', 'Indian',
    'Italian', 'Japanese', 'Mediterranean', 'Mexican', 'Moroccan', 'Spanish', 'Thai',
    'Turkish', 'Vietnamese']
    # list of cuisines under BBC Good Food search
    search_cuisisnes = ['African', 'American', 'Asian', 'Australian', 'Austrian', 'Balinese',
    'Belgian', 'Brazilian', 'British', 'Cajun & Creole', 'Caribbean', 'Chilean', 'Chinese',
    'Cuban', 'Danish', 'Eastern European', 'English', 'French', 'German', 'Greek',
    'Hungarian', 'Indian', 'Irish', 'Italian', 'Japanese', 'Jewish', 'Korean',
    'Latin American', 'Mediterranean', 'Mexican', 'Middle Eastern', 'Moroccan',
    'North African', 'Portuguese', 'Scandinavian', 'Scottish', 'Southern & Soul',
    'Spanish', 'Swedish', 'Swiss', 'Thai', 'Tunisian', 'Turkish', 'Vietnamese']
    # get recipe details for all cuisines
    cuisine_dataframe = get_cuisine_recipes(search_cuisisnes, cuisines)
    # save pandas dataframe in pickle format
    save_obj(cuisine_dataframe, "recipes_data_bbc_good_food")
