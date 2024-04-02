# Use requests to get the data from the database
import requests

db_base_url = 'http://127.0.0.1:5000'

def get_categories():
    response = requests.get(f'{db_base_url}/category')
    data = response.json()
    return data

def get_items(ids=None,categories=None):
    params = {
        'id': ids,
        'category': categories,
    }
    response = requests.get(f'{db_base_url}/item', params=params)
    data = response.json()
    return data

def purchase_item(id,quantity):

    headers = {
    'Content-type':'application/json', 
    'Accept':'application/json'
    }

    data = {
        'id': id,
        'quantity': quantity,
    }
    response = requests.post(f'{db_base_url}/item/purchase', json=data, headers=headers)
    print(response)
    print(response.text)
    response_json = response.json()
    return response_json