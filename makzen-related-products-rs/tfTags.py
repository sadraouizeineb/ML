import pandas as pd
import mysql.connector
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
from sqlalchemy import create_engine

# create a connection to your MySQL database
cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1', database='ecomm')

# specify the SQL query to retrieve data from your table
query = """
    SELECT p.id_produit, p.brand, p.category_id_categorie_produit, p.libelle_produit, c.categorie, t.tags
   FROM produit p
   JOIN categorie_produit c ON p.category_id_categorie_produit = c.id_categorie_produit
  JOIN produit_tags t ON p.id_produit = t.produit_id_produit
"""

# read the data from the table into a pandas DataFrame
df = pd.read_sql(query, con=cnx)
# create a tf-idf vectorizer object
# remove stopwords automatically
tfidf = TfidfVectorizer(max_features=2000)

# create a data matrix from the overviews
X = tfidf.fit_transform(df['tags'])


# create a dictionary mapping product names to their corresponding row index in the DataFrame
product2idx = pd.Series(df.index, index=df['libelle_produit'])


# create a function that generates recommendations
def recommend(libelle_produit):
  
  # get the row in the dataframe for this movie
  idx = product2idx[libelle_produit]
  if type(idx) == pd.Series:
    idx = idx.iloc[0]
    # print("idx:", idx)

  # calculate the pairwise similarities for this movie
  query = X[idx]
  scores = cosine_similarity(query, X)

  # currently the array is 1 x N, make it just a 1-D array
  scores = scores.flatten()

  # update scores for movies with "romance" tag
  for i, tag in enumerate(df['tags']):
    if "SMARTPHONE" in tag.lower():
     scores[i] = 0

  # get the indexes of the highest scoring movies
  # get the first K recommendations
  # don't return itself!
  recommended_idx = (-scores).argsort()[1:6]

  # return the titles of the recommendations
  return df['id_produit'].iloc[recommended_idx]

print("\n Recommendations for 'Samsung Galaxy A10':")
print(recommend('Samsung Galaxy A10'))