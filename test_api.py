import requests

# Define the base URL for API requests
BASE_URL = 'http://localhost:5000'

def test_update_list(token, list_id):
    url = f'{BASE_URL}/lists/{list_id}'
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'items': ['Updated Milk', 'Updated Eggs']
    }
    response = requests.put(url, json=data, headers=headers)
    print(f'Update List: {response.status_code} - {response.text}')

def test_delete_list(token, list_id):
    url = f'{BASE_URL}/lists/{list_id}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.delete(url, headers=headers)
    print(f'Delete List: {response.status_code} - {response.text}')

def test_cleanup(token):
    # Delete test data
    url = f'{BASE_URL}/lists'
    headers = {'Authorization': f'Bearer {token}'}
    lists = requests.get(url, headers=headers).json()
    for l in lists:
        requests.delete(f"{url}/{l['id']}", headers=headers)
    print('Cleaned up test data')
