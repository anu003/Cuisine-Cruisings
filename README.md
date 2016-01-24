# Cuisine Cruisings

### Cuisine similarity analysis between various internaltional cuisines

Why do people like some cuisines and not so much some others? Is this due to similarity in flavour profiles for different cuisines?

## Project Summary
The inspiration for this project comes from my motivation to answer the following questions using data-driven and quantitative methods:
- How can various international cuisines be compared to each other based on the ingredients used, in other words, how similar or dissimilar are cuisines?
- Also, given a person’s interest in a cuisine, how can a valid recommendation be made for other similar cuisines?

Using a database of recipes obtained from online recipe repositories, I have investigated the similarity of various cuisines in terms of ingredient combinations.  Finally, for any given cuisine, using the findings from this analysis, I recommend recipes of the most similar cuisines, not the same cuisine but of the similar cuisines.

## Table of Contents
* [Data Collection and Storage](https://github.com/prathi019/Cuisine-Cruisings/tree/master#data-collection-and-storage)
* [EDA and Feature engineering](https://github.com/prathi019/Cuisine-Cruisings/blob/master/README.md#eda-and-feature-engineering)
* [Model development](https://github.com/prathi019/Cuisine-Cruisings/blob/master/README.md#model-development)
* [Visualization and web development](https://github.com/prathi019/Cuisine-Cruisings/blob/master/README.md#visualization-and-web-development)

## Data Collection and Storage
###### [data collection and storage](https://github.com/prathi019/Cuisine-Cruisings/tree/master/code/web_scrape) & [data cleaning and merging](https://github.com/prathi019/Cuisine-Cruisings/tree/master/code/data_cleaning_and_eda)

Using Python, BeautifulSoup and AWS EC2, web scrape [data scources]() to collect raw text, lists, and other information from html.
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
The following classifier models were used to build a classifier model based on the TF-IDF vectors: Logistic Regression, Random Forest Classifier, Ada Boost Classifier, Multinomial Naive Bayes. After GridSearch, below is a comparison of the performance of these four models, for various preformance metrics.

![Wolrd map](https://github.com/prathi019/Cuisine-Cruisings/blob/master/images/World_map.png)

I choose Logistic Regression based on its higher performance.

In the 28.5K recipe dataset, about 25% of my data was unlabled, and I used the results from this classification model to classify the unlabled data before analysing cuisine similarities.

#### Similarity Analysis
For similarity analysis, I combined all the recipes for each cuisine into one vector and computed the pairwise distance metrics for all cuisines using the following pairwise distance metrics:
scikit-learn: cityblock, cosine, euclidean, l1, l2, manhattan
scipy.spatial.distance:  braycurtis, canberra, chebyshev, correlation, jaccard, matching, yule

I finally went with 'braycurtis' metric because of the most sense it made for most cuisines. The following are some of the interesting findings of the similarity analysis:
              Cuisine             |                                   Interesting Similar Cuisines
--------------------------------- | ---------------------------------------------------------------------------------------------------
'Thai and South-east Asian'       |                          'Central/South American/Caribbean', 'Mexican'
          'Indian'                |                          'Central/South American/Caribbean', 'Mexican'
         'African'                |    'Turkish and Middle Eastern', 'Mediterranean', 'Greek', 'Spanish/Portuguese', 'Italian'
         'Mexican'                |       'Southwestern/Soul Food', 'American', 'Turkish and Middle Eastern', 'Cajun/Creole'
        'European'                |'Eastern European/Russian', 'American', 'English/Scottish', 'French', 'Southwestern/Soul Food'
'Central/South American/Caribbean'|'Mexican', 'Southwestern/Soul Food', 'American', 'Cajun/Creole', 'Turkish and Middle Eastern'
        'Cajun/Creole'            |'Southwestern/Soul Food', 'Central/South American/Caribbean', 'American', 'Mexican', 'Eastern European/Russian'

## Visualization and web development

![Wolrd map](https://github.com/prathi019/Cuisine-Cruisings/blob/master/images/World_map.png)


## Possible Next Steps


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
* [sklearn](http://scikit-learn.org/stable/)
* [scipy](http://www.scipy.org/), [numpy](http://www.scipy.org/)
* [pickle](https://docs.python.org/2/library/pickle.html)
* [flask](http://flask.pocoo.org/)
* [math](https://docs.python.org/2/library/math.html), [string](https://docs.python.org/2/library/string.html), [re](https://docs.python.org/2/library/re.html)
* [collections](https://docs.python.org/2/library/collections.html), [itertools](https://docs.python.org/2/library/itertools.html)

other tools used:
* [bootstrap](http://getbootstrap.com/) - for web-app
* [EC2](https://aws.amazon.com/ec2/) - for web scraping and model running
* [S3](https://aws.amazon.com/s3/) - for data back-up
* [Ammap](https://www.amcharts.com/javascript-maps/) - interactive javascript maps for visualization

## Glossary of Fancy Terms
TFIDF - [Term Frequency - Inverse Document Frequency](http://scikit-learn.org/stable/modules/feature_extraction.html)

