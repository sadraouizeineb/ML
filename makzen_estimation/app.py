from flask import Flask, request, jsonify
from flask_cors import CORS,cross_origin
import pandas as pd
import numpy as np
import pickle

# Load the linear regression model from the .pkl file
with open('linearregression.pkl', 'rb') as f:
    olsmod2 = pickle.load(f)
model=pickle.load(open('LinearRegression.pkl','rb'))

# Load the data from CSV file ( heedha l fih l sscrapping taa tunisianet et mytech)
data = pd.read_csv("data.csv")
# Convert the 'Name' column to a string type
data['Name'] = data['Name'].astype(str)

# Drop any rows that contain NaN values in the 'Price' column
data = data.dropna(subset=['Price'])

# Convert the 'Price' column to a float type( lezm bch njm nlwj aal price )
data['Price'] = data['Price'].astype(float)

app = Flask(__name__)
cors = CORS(app, origins='*')

@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
#     Extract input variables from the POST request (hthom maw taarf ml utilisateur )
    screen_size= request.form.get('screen_size')
    print(screen_size)
    selfie_camera_mp = request.form.get('selfie_camera_mp')
    print(selfie_camera_mp)
    int_memory = request.form.get('int_memory')
    print(int_memory)
    days_used = request.form.get('days_used')
    print(days_used)
    phone_name =request.form.get('phone_name')
    print(phone_name)
    fourg_yes =request.form.get('fourg_yes')
    print(fourg_yes)
    fiveg_yes = request.form.get('fiveg_yes')
    print(fiveg_yes)

    

   
    # Search for the phone in the CSV file
    # filtered_data = data[data["Name"].str.contains(str(phone_name), case=False)]
    # print(data["Name"].str.contains(phone_name, case=False))
    filtered_data = data[data["Name"].str.contains(phone_name, case=False)]

    print(f"Filtered data length: {len(filtered_data)}, Phone name: {filtered_data}")
    # Check if the phone was found
    if len(filtered_data) == 0:
        return jsonify({'errorr': f"{phone_name} not found ."})
    else:
        # Get the price of the phone
        price = filtered_data.iloc[0]["Price"]
        # Calculate the transformed price
        transform_new_price = np.cbrt(price)
        print(transform_new_price)

        # Create the input matrix for the linear regression model
        x_pred = [[1.0954, screen_size, selfie_camera_mp, int_memory, days_used, transform_new_price, fourg_yes, fiveg_yes]]
       #  x_pred=olsmod2.predict(pd.DataFrame(columns=['const', 'screen_size', 'selfie_camera_mp', 'int_memory','days_used','transform_new_price','4g_yes', '5g_yes'],
       #                        data=np.array([1.0954,screen_size,selfie_camera_mp,int_memory,days_used,transform_new_price,fourg_yes,fiveg_yes]).reshape(1, 8)))
       #  print(x_pred)
       #  prediction = (x_pred)**3
        # Make a prediction with the linear regression model
        prediction = olsmod2.predict(x_pred)**3+ (0.0225*price)
        return str((np.round(prediction[0])))

if __name__ == '__main__':
    app.run(debug=True)


#     screen_size = float(request.form.get('screen_size'))
#     selfie_camera_mp = int(request.form.get('selfie_camera_mp'))
#     int_memory = int(request.form.get('int_memory'))
#     days_used = int(request.form.get('days_used'))
#     phone_name = request.form.get('phone_name')
#     print(phone_name)
#     fourg_yes = int(request.form.get('4g_yes'))
#     fiveg_yes = int(request.form.get('5g_yes'))
