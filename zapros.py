import requests
# запрос на загрузку csv
url = 'http://127.0.0.1:8000/upload_route'
files = {'csv_file': open('example.csv', 'rb')}  # Укажите путь к вашему CSV файлу

response = requests.post(url, files=files)

print(response.text)