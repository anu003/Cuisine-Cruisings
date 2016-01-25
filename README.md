# Cuisine Cruisings

### Cuisine similarity analysis between various internaltional cuisines

Why do people like some cuisines and not so much some others? Is it because of the ingredient combinations used in the cuisine, which indicates flavour profile patters?

## Project Summary
The inspiration for this project comes from my motivation to answer the following questions using data-driven and quantitative methods:
- How can various international cuisines be compared to each other based on the ingredients used, in other words, how similar or dissimilar are cuisines?
- Also, given a person’s interest in a cuisine, how can a valid recommendation be made for other similar cuisines?

Using a database of recipes obtained from online recipe repositories, I have investigated the similarity of various cuisines in terms of ingredient combinations.  Finally, for any given cuisine, using the findings from this analysis, I recommend recipes of the most similar cuisines, not the same cuisine but of the similar cuisines.

## Table of Contents
* [Data Collection and Storage](https://github.com/prathi019/Cuisine-Cruisings/tree/master#data-collection-and-storage)
* [EDA and Feature engineering](https://github.com/prathi019/Cuisine-Cruisings/blob/master/README.md#eda-and-feature-engineering)
* [Model development](https://github.com/prathi019/Cuisine-Cruisings/blob/master/README.md#model-development)
* [Visualization and web application](https://github.com/prathi019/Cuisine-Cruisings/blob/master/README.md#visualization-and-web-application)
* [Possible Next Steps](https://github.com/prathi019/Cuisine-Cruisings/blob/master/README.md#possible-next-steps)
* [Toolkit + Credits](https://github.com/prathi019/Cuisine-Cruisings/tree/master#toolkit--credits)

## Data Collection and Storage
###### [data collection and storage](https://github.com/prathi019/Cuisine-Cruisings/tree/master/code/web_scrape) & [data cleaning and merging](https://github.com/prathi019/Cuisine-Cruisings/tree/master/code/data_cleaning_and_eda)

Using Python, BeautifulSoup, Selenium and AWS EC2, I web scraped the recipe databanks from the [data scources](https://github.com/prathi019/Cuisine-Cruisings/tree/master#toolkit--credits) to collect raw text, lists, and other information from html.
Details for each recipe include the following information:
*	Recipe Source (Non-Null) - Epicurious, BBC Food, Chowhound, BBD Good Food, Saveur
*	Recipe Cuisine - 45 different cuisines
*	Recipe Link (Non-Null) - url to recipes
*	Recipe Name (Non-Null) - title of recipe
*	Recipe Author/Chef - author/chef who put up the recipe
*	Recipe Rating/Recommendations - ratings and/or recommendations for recipe
*	Recipe Description - short description/summary of recipe
*	Recipe Ingredients List (Non-Null) - list of ingredients and amounts used in recipe
*	Recipe Preparation Steps (Non-Null) - preperation steps involved in recipe
*	Recipe Prep Time - prep time required for recipe
*	Recipe Cooking Time - cooking time required for recipe
*	Total Nutrition - nutrtional value of recipe
* Recipe Image Source - url to recipe image

Data from all sources is cleaned to replace all non-ascii content with their corresponding values and merged into one database of over 28K recipes. Scraped data and cleaned data is stored in MongoDB, pandas dataframe in pickled file and S3 for backup.

## EDA and Feature engineering
###### [ingredient vectorizer]()
For balanced distribution of number of recipes per cuisine and better signal, the cuisines were grouped together, based on geographical closeness of cuisines, into 19 unique cuisines.

The next step is quite possibly the most time-consuming, challenging, and rewarding part of the project. Using NLTK tokennization, lemmatizing, stop-words, bi-gram model and a custom built n-gram model, a list of unique ingredient names was extracted from the list of ingredients for each recipe. From these ingredient names, I generated a bag of unique ingredients for all recipes in the database. The ingredients were converted into count vectors and TF-IDF vectors based on these unique bag of words. For modeling, any ingredient which had less than two occurences in all the recipes were not considered.

## Model development
#### Classification Model
The following classifier models were used to build a classifier model based on the TF-IDF vectors: Logistic Regression, Random Forest Classifier, Ada Boost Classifier, Multinomial Naive Bayes. Below is a comparison of the performance of these four models, after GridSearch, for various preformance metrics.

![Comparison of classifier models](https://github.com/prathi019/Cuisine-Cruisings/blob/master/images/Compare_classif_models.png)

I choose Logistic Regression based on its higher performance.

In the 28.5K recipe dataset, about 25% of my data was unlabled, and I used the results from this classification model to classify the unlabled data before analysing cuisine similarities.

#### Similarity Analysis
For similarity analysis, I combined all the recipes for each cuisine into one vector and computed the pairwise distance metrics for all cuisines using the following pairwise distance metrics:
scikit-learn: cityblock, cosine, euclidean, l1, l2, manhattan
scipy.spatial.distance:  braycurtis, canberra, chebyshev, correlation, jaccard, matching, yule

I finally went with 'braycurtis' metric because of the most sense it made for most cuisines. The following are some of the interesting findings of the similarity analysis:

| Cuisine | Interesting Similar Cuisines |
| :-----------------------: | :--------------------: |
| Cajun/Creole                     | Mexican, Eastern European/Russian |
| Indian                           | Central/South American/Caribbean, Mexican |
| African                          | Spanish/Portuguese, Italian |
| Mexican                          | Turkish and Middle Eastern, Cajun/Creole |
| Central/South American/Caribbean | Cajun/Creole, Turkish and Middle Eastern |

#### Similar Cuisine Recipe Recommendations
Using the results from the similarity analysis, the recommendations model recommends similar cuisine recipes for any selected cuisine and a set of ingredients.

When a cuisine is selected, the search box (on the next page) displays only the ingredients that have been seen for the cuisine in the database. When a set of ingredients are selcted, they are converted into a vector and compared to all the recipes in the top 5 similar cuisines group for that cuisine. The top 20 results are displayed in ascending order of the distance between the given search vector and each of the compared recipes. 

## Visualization and web application

![Wolrd map](https://github.com/prathi019/Cuisine-Cruisings/blob/master/images/World_map.png)
![World map with ballon text](https://github.com/prathi019/Cuisine-Cruisings/blob/master/images/World_map_balloon.png)
![US map with star](https://github.com/prathi019/Cuisine-Cruisings/blob/master/images/US_star.png)

## Possible Next Steps
* Equally distributed data - Since two of my data sources were from the BBC group, a disproportionate portion of my data has English/Scottish recipes. For future work, I would like to get more data to get an equally distributed dataset
* Other recipe details (cooking time, cooking methods, nutritional value) - I would also like to use other recipe details to improve the performance of my models, as well as my recommendations.
* Historical colonization data and spice routes - For this project I validated my results based on what made intuitive sense. For future work, I would like to use historical colonization data as well as spice routes data to validate the results of my similarity analysis model.

## Toolkit + Credits
data sources:
* [Epicurious](http://www.epicurious.com/recipesmenus)
* [BBC Food](http://www.bbc.co.uk/food/recipes)
* [Chowhound](http://www.chowhound.com/recipes)
* [BBC Good Food](http://www.bbcgoodfood.com/recipes)
* [Saveur](http://www.saveur.com/recipes)

langugages used:
* python
* bash
* html / javascript / css

python libraries used:
* [pandas](http://pandas.pydata.org/pandas-docs/version/0.17.1/index.html)
* [nltk](http://www.nltk.org/)
* [requests](http://docs.python-requests.org/en/latest/)
* [beautifulsoup](http://www.crummy.com/software/BeautifulSoup/)
* [selenium](http://selenium-python.readthedocs.org/)
* [pymongo](https://docs.mongodb.org/getting-started/python/client/) - Chosen because my database operations involve more dumping recipe details in and pulling details out than creating complex queries.
* [matplotlib](http://matplotlib.org/)
* [seaborn](http://stanford.edu/~mwaskom/software/seaborn/)
* [sklearn](http://scikit-learn.org/stable/)
* [scipy](http://www.scipy.org/), [numpy](http://www.scipy.org/)
* [pickle](https://docs.python.org/2/library/pickle.html)
* [flask](http://flask.pocoo.org/)
* [jinja2](http://jinja.pocoo.org/)
* [math](https://docs.python.org/2/library/math.html), [string](https://docs.python.org/2/library/string.html), [re](https://docs.python.org/2/library/re.html)
* [collections](https://docs.python.org/2/library/collections.html), [itertools](https://docs.python.org/2/library/itertools.html)

other tools used:
* [bootstrap](http://getbootstrap.com/) - for web-app
* [EC2](https://aws.amazon.com/ec2/) - for web scraping and model running
* [S3](https://aws.amazon.com/s3/) - for data back-up
* [ammap](https://www.amcharts.com/javascript-maps/) - interactive javascript maps for visualization

## Glossary of Fancy Terms
TFIDF - [Term Frequency - Inverse Document Frequency](http://scikit-learn.org/stable/modules/feature_extraction.html)
