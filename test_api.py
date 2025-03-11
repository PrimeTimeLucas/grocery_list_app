import requests

# Define the base URL for API requests
BASE_URL = 'http://localhost:5000'

def test_create_list(token):
    url = f'{BASE_URL}/lists'
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'store_name': 'Test Supermarket',
        'items': [
            {
                'name': 'Milk',
                'price': 2.99
            },
            {
                'name': 'Eggs',
                'price': 3.49,
                'store': 'Farm Fresh'
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    print(f'Create List: {response.status_code} - {response.text}')
    if response.status_code == 201:
        return response.json()['id']
    return None

def test_update_list(token, list_id):
    url = f'{BASE_URL}/lists/{list_id}'
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'store_name': 'Updated Supermarket',
        'items': [
            {
                'name': 'Updated Milk',
                'price': 3.99
            },
            {
                'name': 'Updated Eggs',
                'price': 4.49
            }
        ]
    }
    response = requests.put(url, json=data, headers=headers)
    print(f'Update List: {response.status_code} - {response.text}')

def test_get_list(token, list_id):
    url = f'{BASE_URL}/lists/{list_id}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    print(f'Get List: {response.status_code}')
    if response.status_code == 200:
        print(f'List details: {response.json()}')
    else:
        print(f'Error: {response.text}')

def test_delete_list(token, list_id):
    url = f'{BASE_URL}/lists/{list_id}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.delete(url, headers=headers)
    print(f'Delete List: {response.status_code} - {response.text}')

def test_monthly_stats(token):
    url = f'{BASE_URL}/stats/monthly'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    print(f'Monthly Stats: {response.status_code}')
    if response.status_code == 200:
        print(f'Stats: {response.json()}')
    else:
        print(f'Error: {response.text}')

def test_cleanup(token):
    # Delete test data
    url = f'{BASE_URL}/lists'
    headers = {'Authorization': f'Bearer {token}'}
    lists = requests.get(url, headers=headers).json()
    for l in lists:
        requests.delete(f"{url}/{l['id']}", headers=headers)
    print('Cleaned up test data')

def run_all_tests(token):
    # Create a list and get its ID
    list_id = test_create_list(token)
    if list_id:
        # Test getting the list details
        test_get_list(token, list_id)
        
        # Test updating the list
        test_update_list(token, list_id)
        
        # Get updated list details
        test_get_list(token, list_id)
        
        # Test monthly stats
        test_monthly_stats(token)
        
        # Clean up by deleting the list
        test_delete_list(token, list_id)
