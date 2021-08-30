from itertools import count

import requests


def get_vacancies_amount(language='Python'):
    url = 'https://api.hh.ru/vacancies'

    payload = {
        'text': 'программист {0}'.format(language),
        'area': 1,
        'period': 30,
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()

    return response.json()['found']


def predict_rub_salary(vacancy):
    salary = vacancy.get('salary')
    if not salary or salary['currency'] != 'RUR':
        return None
    if salary['from'] and salary['to']:
        return (salary['from'] + salary['to']) / 2
    if salary['from']:
        multiplier_coef = 1.2
        return salary['from'] * multiplier_coef
    if salary['to']:
        multiplier_coef = 0.8
        return salary['to'] * multiplier_coef


def get_average_salary(language='Python'):
    url = 'https://api.hh.ru/vacancies'

    vacancies = []
    for page in count(0):

        payload = {
            'text': 'программист {0}'.format(language),
            'area': 1,
            'period': 30,
            'page': page,
        }

        response = requests.get(url, params=payload)
        response.raise_for_status()
        if page >= response.json()['pages'] - 1:
            break

        vacancies.extend(response.json()['items'])

    vacancy_salaries = []
    for vacancy in vacancies:
        salary = predict_rub_salary(vacancy)
        vacancy_salaries.append(salary)

    vacancy_salaries = list(filter(lambda salary: salary, vacancy_salaries))

    average_salary = sum(vacancy_salaries) / len(vacancy_salaries)
    vacancies_processed = len(vacancy_salaries)
    return average_salary, vacancies_processed


def main():
    languages = ['Ruby', 'Swift']  # , 'C', 'C#', 'Java', 'JavaScript', 'PHP', 'R', 'Python', 'C++']

    languages_statistic = {}
    for language in languages:
        average_salary, vacancies_processed = get_average_salary(language)
        languages_statistic[language] = {
            'vacancies_found': get_vacancies_amount(language),
            'vacancies_processed': vacancies_processed,
            'average_salary': int(average_salary),
        }

    print(languages_statistic)


if __name__ == '__init__':
    main()
