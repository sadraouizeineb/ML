from flask import Flask, jsonify, request
import pandas as pd
import mysql.connector
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for the app
cors = CORS(app, origins='*')
# Create a connection to your MySQL database
cnx = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='ecomm')
# cnx = mysql.connector.connect(
# host="mysqldb",
# port="3306",
# database="ecomm",
# user="root",
# password="root"
# )

# Specify the SQL query to retrieve data from your table
query = """
    SELECT p.id_produit, p.brand, p.category_id_categorie_produit, p.libelle_produit, c.categorie, t.tags, p.prix_unitaire, p.image_url, p.description,p.code_produit
    FROM produit p
    JOIN categorie_produit c ON p.category_id_categorie_produit = c.id_categorie_produit
    JOIN produit_tags t ON p.id_produit = t.produit_id_produit
"""

# Read the data from the table into a pandas DataFrame
df = pd.read_sql(query, con=cnx)

# Create a tf-idf vectorizer object
# Remove stopwords automatically
tfidf = TfidfVectorizer(max_features=2000)

# Create a data matrix from the tags
X = tfidf.fit_transform(df['tags'])

# Create a dictionary mapping product names to their corresponding row index in the DataFrame
product2idx = pd.Series(df.index, index=df['libelle_produit'])

# Create a function that generates recommendations
# Create a function that generates recommendations
def recommend(libelle_produit):
  
  # Get the row in the DataFrame for this product
  idx = product2idx[libelle_produit]
  if type(idx) == pd.Series:
    idx = idx.iloc[0]

  # Calculate the pairwise similarities for this product
  query = X[idx]
  scores = cosine_similarity(query, X)

  # Currently the array is 1 x N, make it just a 1-D array
  scores = scores.flatten()

  # Get the indexes of the highest scoring products
  # Get the first K recommendations
  # Don't return itself!
  recommended_idx = (-scores).argsort()[1:6]

  # Return the IDs of the recommendations
  return df['id_produit'].iloc[recommended_idx].tolist()



@app.route('/recommend', methods=['POST'])
def make_recommendation():
    data = request.get_json()
    libelle_produit = data['libelle_produit']
    recommendations = recommend(libelle_produit)
    # Return the IDs of the recommendations
    return jsonify(recommendations)



if __name__ == '__main__':
    app.run(debug=True, port=5002)

