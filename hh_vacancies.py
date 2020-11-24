import requests
from itertools import count
from utils import predict_rub_salary, calc_date_one_month_ago, print_stats_table
from utils import POPULAR_PROGRAMMING_LANGS


HH_VACANCIES_URL = "https://api.hh.ru/vacancies"
HH_MOSCOW_AREA = 1


def predict_rub_salary_for_hh(vacancy):
    if not vacancy["salary"]:
        return None
    elif vacancy["salary"]["currency"] != "RUR":
        return None
    else:
        return predict_rub_salary(vacancy["salary"]["from"], vacancy["salary"]["to"])


def get_hh_vacancies():
    vacancies_stats = {}
    date_from = calc_date_one_month_ago().strftime("%Y-%m-%d")

    for lang in POPULAR_PROGRAMMING_LANGS:
        params = {"area": HH_MOSCOW_AREA, "text": f"(программист* OR разработчик*) AND ({lang})",
                  "date_from": date_from}
        founded_vacancies = []
        found = 0
        for page in count(0):
            params["page"] = page
            page_response = requests.get(HH_VACANCIES_URL, params=params)
            page_response.raise_for_status()
            page_of_vacancies = page_response.json()
            found = page_of_vacancies["found"]
            if page >= page_of_vacancies["pages"] - 1:
                break
            founded_vacancies += page_of_vacancies["items"]
        vacancies_salary = []
        for vacancy in founded_vacancies:
            rub_salary = predict_rub_salary_for_hh(vacancy)
            if rub_salary:
                vacancies_salary.append(rub_salary)
        vacancies_stats[lang] = {"vacancies_found": found, "vacancies_processed": len(
            vacancies_salary), "average_salary": int(sum(vacancies_salary) / len(vacancies_salary))}

    print_stats_table(vacancies_stats, "HeadHuner Moscow")