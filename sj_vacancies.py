import requests
from itertools import count
from dotenv import load_dotenv
import os
from utils import predict_rub_salary, calc_date_one_month_ago, print_stats_table
from utils import POPULAR_PROGRAMMING_LANGS


SJ_VACANCIES_URL = "https://api.superjob.ru/2.0/vacancies"
SJ_MOSCOW_TOWN = 4


def predict_rub_salary_for_sj(vacancy):
    if vacancy["currency"] != "rub":
        return None
    if (vacancy["payment_from"] == 0) & (vacancy["payment_from"] == 0):
        return None
    return predict_rub_salary(vacancy["payment_from"], vacancy["payment_to"])


def get_sj_vacancies():
    load_dotenv()
    sj_token = os.getenv('SJ_TOKEN')
    headers = {"X-Api-App-Id": sj_token}
    date_from = calc_date_one_month_ago().strftime('%s')
    params = {"town": SJ_MOSCOW_TOWN, "catalogues": 48,
              "count": 100, "date_published_from": date_from}
    founded_vacancies = []
    for page in count(0):
        params["page"] = page
        response = requests.get(
            SJ_VACANCIES_URL, headers=headers, params=params)
        page_of_vacancies = response.json()
        for vacancy in page_of_vacancies["objects"]:
            founded_vacancies.append(
                {"profession": vacancy['profession'], "salary": predict_rub_salary_for_sj(vacancy)})
        if not page_of_vacancies["more"]:
            break

    vacancies_stats = {}
    for lang in POPULAR_PROGRAMMING_LANGS:
        vacancies_found = 0
        vacancies_salary = []
        for vacancy in founded_vacancies:
            if lang in vacancy["profession"]:
                vacancies_found += 1
                if vacancy["salary"]:
                    vacancies_salary.append(vacancy["salary"])
        average_salary = int(sum(
            vacancies_salary) / len(vacancies_salary)) if len(vacancies_salary) > 0 else None
        vacancies_stats[lang] = {"vacancies_found": vacancies_found, "vacancies_processed": len(
            vacancies_salary), "average_salary": average_salary}

    print_stats_table(vacancies_stats, "SuperJob Moscow")
