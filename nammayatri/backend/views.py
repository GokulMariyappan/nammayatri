from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from .models import CustomUser
from django.shortcuts import get_object_or_404
# Create your views here.
import requests
from datetime import datetime
import pytz  # For timezone handling
import pandas as pd
import joblib
from asgiref.sync import async_to_sync
import os
from django.conf import settings


def myfuc():
# --- 1. Get Current Date/Time (Bangalore Time) ---
    bangalore_tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(bangalore_tz)

    # Process temporal features
    hour = current_time.hour
    day_of_week = current_time.weekday()  # 0=Monday, 6=Sunday
    month = current_time.month
    is_weekend = 1 if day_of_week >= 5 else 0

    # # --- 2. Get Rain Status from OpenWeatherMap API ---
    # API_KEY = "YOUR_API_KEY"  # Get from https://openweathermap.org/api
    # CITY = "Bengaluru,IN"

    # def is_raining(api_key, city):
    #     base_url = "http://api.openweathermap.org/data/2.5/weather"
    #     params = {
    #         "q": city,
    #         "appid": api_key,
    #         "units": "metric"
    #     }
        
    #     response = requests.get(base_url, params=params).json()
        
    #     # Check for rain in weather conditio, 'ns
    #     rain_codes = [500, 501, 502, 503, 504, 511, 520, 521, 522, 531]  # Rain-related weather codes
    #     current_weather = response.get('weather', [{}])[0]
        
    #     # Check both weather ID and 'rain' key
    #     return (
    #         current_weather.get('id') in rain_codes or
    #         'rain' in current_weather.get('main'').lower() or
    #         response.get('rain') is not None
    #     )

    # # Get rainfall status
    # is_rain = 1 if is_raining(API_KEY, CITY) else 0
    # rainfall = response.get('rain', {}).get('1h', 0) if is_rain else 0  # Get mm of rain in last hour

    

    # Load the model and feature names **once** at the top (avoiding reload on every request)
    # --- 3. Prepare Features for Model ---
    # Correct file paths using BASE_DIR

    # Debugging: Print the expected paths

    # Load the files
    model = joblib.load('commuter_model_ward.pkl')
    feature_names = joblib.load('feature_names_ward.pkl')

    print("Model and feature names loaded successfully!")
    # example output
    rainfall=0
    is_rain="no"

    # --------------------------------changes done down here -----------------------------------------

    # dictionary to store the output data
    dic={}

    # i = ward number
    for  i in range(243):
        input_data = pd.DataFrame([[
            i,
            hour,
            day_of_week,
            is_weekend,
            rainfall,
            month
        ]], columns=feature_names)
        prediction = model.predict(input_data)
        dic[i]=prediction

    return dic



class ModelTesting(View):

    bengaluru_wards = {
    1: "Kempegowda Ward",
    2: "Chowdeshwari Ward",
    3: "Atturu",
    4: "Yelahanka Satellite Town",
    5: "Jakkuru",
    6: "Thanisandra",
    7: "Byatarayanapura",
    8: "Kodigehalli",
    9: "Vidyaranyapura",
    10: "Doddabommasandra",
    11: "Kuvempu Nagar",
    12: "Shettihalli",
    13: "Mallasandra",
    14: "Bagalakunte",
    15: "T. Dasarahalli",
    16: "Jalahalli",
    17: "J.P. Park",
    18: "Radhakrishna Temple Ward",
    19: "Sanjay Nagar",
    20: "Ganga Nagar",
    21: "Hebbal",
    22: "Vishwanath Nagenahalli",
    23: "Nagavara",
    24: "HBR Layout",
    25: "Horamavu",
    26: "Ramamurthy Nagar",
    27: "Banaswadi",
    28: "Kammanahalli",
    29: "Kacharakanahalli",
    30: "Kadugondanahalli",
    31: "Kushal Nagar",
    32: "Kaval Byrasandra",
    33: "Manorayanapalya",
    34: "Gangenahalli",
    35: "Aramane Nagar",
    36: "Malleswaram",
    37: "Kadu Malleshwara",
    38: "Subramanya Nagar",
    39: "Nagapura",
    40: "Mahalakshmipuram",
    41: "Laggere",
    42: "Nandini Layout",
    43: "J.P. Park",
    44: "Yeshwanthpura",
    45: "H.M.T. Ward",
    46: "Chokkasandra",
    47: "Dodda Bidarakallu",
    48: "Peenya Industrial Area",
    49: "Rajagopal Nagar",
    50: "Lakshmidevi Nagar",
    51: "Nagarbhavi",
    52: "Jnanabharathi",
    53: "Ullalu",
    54: "Kottegepalya",
    55: "Shivanagara",
    56: "Kethamaranahalli",
    57: "Srirampura",
    58: "Okalipuram",
    59: "Dayananda Nagar",
    60: "Prakash Nagar",
    61: "Rajajinagar",
    62: "Basaveshwaranagar",
    63: "Kamakshipalya",
    64: "Vrisabhavathi Nagar",
    65: "Kaveripura",
    66: "Kempapura Agrahara",
    67: "Jagajeevanram Nagar",
    68: "Rayapuram",
    69: "Chickpet",
    70: "KR Market",
    71: "Dharmaraya Swamy Temple",
    72: "Cottonpet",
    73: "Binnypet",
    74: "Chamrajpet",
    75: "Azad Nagar",
    76: "Sunkenahalli",
    77: "Vishveshwara Puram",
    78: "Siddapura",
    79: "Hombegowda Nagar",
    80: "Lakkasandra",
    81: "Adugodi",
    82: "Ejipura",
    83: "Varthur",
    84: "Bellandur",
    85: "Kadubeesanahalli",
    86: "Hoodi",
    87: "Garudacharpalya",
    88: "Mahadevapura",
    89: "Doddanekkundi",
    90: "Marathahalli",
    91: "HAL Airport",
    92: "Jeevanbhimanagar",
    93: "New Thippasandra",
    94: "Domlur",
    95: "Konena Agrahara",
    96: "Vignan Nagar",
    97: "Hagadur",
    98: "Dodda Bommasandra",
    99: "Kadugodi",
    100: "Kannamangala",
    101: "K.R. Puram",
    102: "Basavanapura",
    103: "Horamavu Agara",
    104: "Kalkere",
    105: "Amruthahalli",
    106: "Shivaji Nagar",
    107: "Vasanth Nagar",
    108: "Tasker Town",
    109: "Sudham Nagar",
    110: "Sampangiram Nagar",
    111: "Bharathi Nagar",
    112: "Frazer Town",
    113: "Pulakeshinagar",
    114: "Sagayarapuram",
    115: "Ulsoor",
    116: "Jayanagar",
    117: "Basavanagudi",
    118: "Gandhi Bazaar",
    119: "Thyagarajanagar",
    120: "Banashankari",
    121: "Uttarahalli",
    122: "Padmanabhanagar",
    123: "Yelachenahalli",
    124: "J.P. Nagar",
    125: "Puttenahalli",
    126: "Hulimavu",
    127: "Bommanahalli",
    128: "Begur",
    129: "Singasandra",
    130: "Hosa Road",
    131: "Parappana Agrahara",
    132: "Electronic City",
    133: "Bangalore South",
    134: "Anekal",
    135: "Jigani",
    136: "Bannerghatta",
    137: "Hesaraghatta",
    138: "Dasarahalli",
    139: "Peenya",
    140: "Nelamangala",
    141: "Kanakapura Road",
    142: "Thalagattapura",
    143: "Rajarajeshwari Nagar",
    144: "Kengeri",
    145: "Kumbalgodu",
    146: "Byramangala",
    147: "Sunkadakatte",
    148: "Kammagondanahalli",
    149: "Magadi Road",
    150: "Goripalya",
    151: "Cholurpalya",
    152: "Chandapura",
    153: "Sarjapur",
    154: "Channasandra",
    155: "Hennur",
    156: "Kothanur",
    157: "Dodda Banaswadi",
    158: "Ramamurthy Nagar Ext.",
    159: "Banaswadi Ext.",
    160: "Cox Town",
    161: "Byrasandra",
    162: "C.V. Raman Nagar",
    163: "Hoodi Ext.",
    164: "Bellandur Ext.",
    165: "Srinagar",
    166: "Bapuji Nagar",
    167: "Kaveripura",
    168: "Basaveshwara Nagar",
    169: "Attiguppe",
    170: "Nayandahalli",
    171: "Raja Rajeshwari Nagar",
    172: "Kengeri Ext.",
    173: "Vijayanagar",
    174: "Maruthi Mandir",
    175: "Jayanagar Ext.",
    176: "Koramangala",
    177: "Indiranagar",
    178: "H.S.R. Layout",
    179: "Sarjapur Road",
    180: "Whitefield",
    181: "Kadugodi Ext.",
    182: "Jigani Industrial Area",
    183-243: "Other Wards",
    }


    def get(self, request):
        dic = {}
        data = myfuc()
        for key, value in data.items():
            dic[key] = int(value)
        return JsonResponse({'data' : dic})
        

class HomeView(View):
    def get(self, request):
        return HttpResponse("This works for now")
    
class GetEmail(View):
    def get(self, request, email):
        print('im printing',email)
        user = get_object_or_404(CustomUser, email = email)
        r = {'role' : user.role}
        return JsonResponse(r)
