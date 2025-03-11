def test_cleanup(token):
    # Delete test data
    url = f'{BASE_URL}/lists'
    headers = {'Authorization': f'Bearer {token}'}
    lists = requests.get(url, headers=headers).json()
    for l in lists:
        requests.delete(f"{url}/{l['id']}", headers=headers)
    print('Cleaned up test data')
