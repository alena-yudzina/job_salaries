import os
from itertools import count

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from:
        multiplier_coef = 1.2
        return salary_from * multiplier_coef
    if salary_to:
        multiplier_coef = 0.8
        return salary_to * multiplier_coef


def predict_rub_salary_hh(vacancy):
    salary = vacancy.get('salary')
    if not salary or salary['currency'] != 'RUR':
        return None
    return predict_salary(salary['from'], salary['to'])


def predict_rub_salary_sj(vacancy):
    salary_from = vacancy['payment_from']
    salary_to = vacancy['payment_to']
    currency = vacancy['currency']
    if currency != 'rub':
        return None
    return predict_salary(salary_from, salary_to)


def process_stats_params(vacancies, predict_salary_func):
    vacancy_salaries = []
    for vacancy in vacancies:
        salary = predict_salary_func(vacancy)
        vacancy_salaries.append(salary)

    vacancy_salaries = list(filter(bool, vacancy_salaries))
    if vacancy_salaries:
        average_salary = sum(vacancy_salaries) / len(vacancy_salaries)
    else:
        average_salary = 0
    vacancies_processed = len(vacancy_salaries)
    return average_salary, vacancies_processed


def get_site_stats_hh(token, language='Python'):
    url = 'https://api.hh.ru/vacancies'

    vacancies = []
    moscow_id = 1
    searching_period = 30
    vacancies_per_page = 100
    payload = {
            'text': 'программист {0}'.format(language),
            'area': moscow_id,
            'period': searching_period,
            'per_page': vacancies_per_page,
        }

    for page in count(0):

        payload['page'] = page

        response = requests.get(url, params=payload)
        response.raise_for_status()
        response_body = response.json()
        vacancies.extend(response_body['items'])

        if page >= response_body['pages'] - 1:
            break
    found_vacancies = response_body['found']
    average_salary, vacancies_processed = process_stats_params(vacancies, predict_rub_salary_hh)
    return average_salary, vacancies_processed, found_vacancies


def get_site_stats_sj(token, language='Python'):
    api_url = 'https://api.superjob.ru/2.0/vacancies/'

    searching_period = 30
    it_department_id = 48
    moscow_id = 4
    vacancies_per_page = 100
    serach_position_id = 1

    headers = {
            'X-Api-App-Id': token,
    }

    payload = {
        'period': searching_period,
        'catalogues': it_department_id,
        'town': moscow_id,
        'count': vacancies_per_page,
        'keywords[0][keys]': language,
        'keywords[0][skwc]': 'particular',
        'keywords[0][srws]': serach_position_id,
    }

    vacancies = []

    for page in count(0):

        payload['page'] = page

        response = requests.get(api_url, headers=headers, params=payload)
        response.raise_for_status()
        response_body = response.json()
        vacancies.extend(response_body['objects'])

        if not response_body['more']:
            break
    found_vacancies = response_body['total']
    average_salary, vacancies_processed = process_stats_params(vacancies, predict_rub_salary_sj)
    return average_salary, vacancies_processed, found_vacancies


def create_stats(languages, site_stats_func, token=''):
    languages_stats = {}
    for language in languages:
        average_salary, vacancies_processed, found_vacancies = \
            site_stats_func(token=token, language=language)
        languages_stats[language] = {
            'vacancies_found': found_vacancies,
            'vacancies_processed': vacancies_processed,
            'average_salary': int(average_salary),
        }
    return languages_stats


def create_ascii_table(site, stats):
    table_rows = []
    table_rows.append([
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата',
        ])
    for language, stat in stats.items():
        table_row = [
            language,
            stat['vacancies_found'],
            stat['vacancies_processed'],
            stat['average_salary'],
        ]
        table_rows.append(table_row)
    table = AsciiTable(table_rows)
    table.title = '{0} Moscow'.format(site)
    return table.table


def main():
    load_dotenv()
    token = os.environ['SJ_SECRET_KEY']
    languages = [
        'Ruby', 'Swift', 'C', 'C#',
        'Java', 'JavaScript', 'PHP',
        'R', 'Python', 'C++',
    ]
    sites_stats = {
        'HeadHunter': create_stats(languages, get_site_stats_hh),
        'SuperJob': create_stats(languages, get_site_stats_sj, token),
    }
    for site, stats in sites_stats.items():
        ascii_table = create_ascii_table(site, stats)
        print(ascii_table, end='\n\n')


if __name__ == '__init__':
    main()
