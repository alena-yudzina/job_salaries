import requests


def main():
    url = 'https://api.hh.ru/vacancies'
    payload = {
        'text': 'программист',
        'area': 1,
    }
    response = requests.get(url, params=payload)
    print(response.json())


if __name__ == '__init__':
    main()
