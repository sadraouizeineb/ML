import pandas as pd
import warnings
from sortedcontainers import SortedList
import mysql.connector


# Suppress pandas warning message
warnings.filterwarnings("ignore", message="pandas only support SQLAlchemy connectable")

# Connect to your database
cnx = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='ecomm')
cursor = cnx.cursor()

# number of users
#badel ur.role_id=2 aandek
N = """SELECT max(id) from user u JOIN user_roles ur ON ur.user_id=u.id WHERE ur.role_id=2 """
nbr_user_str = pd.read_sql(N, con=cnx)
nbrUser = nbr_user_str.iloc[0][0]
print("N:", nbrUser)

userID = 3
K = 5 # number of neighbors we'd like to consider
limit = 5 # number of common purchases users must have in common in order to consider
#ba3d ma t3abi db rajaa limit matensech
neighbors = [] # store neighbors in this list

for i in range(nbrUser):
    # find the K closest users to user i
    products_i_query = "SELECT produit_id FROM commande c JOIN detail_commande d ON d.commande_id = c.id_commande WHERE user_id = %s"
    params = (userID,)
    products_i = pd.read_sql(products_i_query, con=cnx,params=params)
    products_i = products_i['produit_id'].tolist()
    products_i_set = set(products_i)
    sl = SortedList()

    for j in range(nbrUser):
      # don't include yourself
      if j != userID:
        products_j_query = """ SELECT produit_id FROM commande c JOIN detail_commande d ON d.commande_id = c.id_commande WHERE user_id= %s"""
        params = (j,)
        products_j = pd.read_sql(products_j_query, con=cnx, params=params)
        products_j = products_j['produit_id'].tolist()
        products_j_set = set(products_j)
        common_purchases = (products_i_set & products_j_set) # intersection
        # Calculate Jaccard index as similarity measure
        intersection = len(products_i_set.intersection(products_j_set))
        union = len(products_i_set.union(products_j_set))
        jaccard_index = intersection / union

#insert into sorted list and truncate
## bech yo93ed kol mara yfasakh a9al wehed similar lil user i hata yo93dou the 25 most similar
        sl.add((-jaccard_index, j))
        if len(sl) > K:
          del sl[-1]

# store the neighbors
        neighbors.append(sl)


def recommend_products(i):
  recommended_products = set()
  # Find the union of all purchased products by neighbors
  for _, j in neighbors[i]:
    products_j_query = """ SELECT produit_id FROM commande c JOIN detail_commande d ON d.commande_id = c.id_commande WHERE user_id= %s"""
    params = (j,)
    products_j = pd.read_sql(products_j_query, con=cnx, params=params)
    recommended_products |= set(products_j['produit_id'])
  # Remove products that the user i has already purchased
  recommended_products -= set(products_i)
  return recommended_products



recommended_products_B = recommend_products(userID)

print(f"Products recommended for user {userID} are: {recommended_products_B}")