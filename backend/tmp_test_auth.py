import requests, json
url='http://127.0.0.1:8000/api/auth/signup'
data={'username':'demo','email':'demo@example.com','password':'demo123','full_name':'Demo User'}
resp=requests.post(url, json=data)
print(resp.status_code)
print(resp.text)
