import requests
import datetime as dt
from terminaltables import AsciiTable
from itertools import count
from dotenv import load_dotenv
import os

HH_VACANCIES_URL = "https://api.hh.ru/vacancies"
SJ_VACANCIES_URL = "https://api.superjob.ru/2.0/vacancies"
POPULAR_PROGRAMMING_LANGS = ["JavaScript",
                             "Java", "Python", "Ruby", "PHP", "C++", "C#", "C", "Go"]
HH_MOSCOW_AREA = 1
SJ_MOSCOW_TOWN = 4


def predict_rub_salary(salary_from, salary_to):
    if (salary_from is not None) & (salary_to is not None):
        return int((salary_from + salary_to) / 2)
    elif (salary_from is None) | (salary_from == 0):
        return int(salary_to * 0.8)
    elif (salary_to is None) | (salary_to == 0):
        return int(salary_from * 1.2)
    else:
        return None


def predict_rub_salary_for_hh(vacancy):
    if vacancy["salary"] is None:
        return None
    elif vacancy["salary"]["currency"] != "RUR":
        return None
    else:
        return predict_rub_salary(vacancy["salary"]["from"], vacancy["salary"]["to"])


def predict_rub_salary_for_sj(vacancy):
    if vacancy["currency"] != "rub":
        return None
    if (vacancy["payment_from"] == 0) & (vacancy["payment_from"] == 0):
        return None
    return predict_rub_salary(vacancy["payment_from"], vacancy["payment_to"])


def calc_date_one_month_ago():
    now = dt.datetime.now()
    last_month = now.month-1 if now.month > 1 else 12
    return dt.datetime(now.year, last_month, now.day)


def print_stats_table(stats, title):
    table_data = [["Язык программирования", "Вакансий найдено",
                   "Вакансий обработано", "Средняя зарплата"]]
    for row in stats:
        row_data = [row]
        for col in stats[row]:
            row_data.append(stats[row][col])
        table_data.append(row_data)
    stats_table_instance = AsciiTable(table_data, title)
    print(stats_table_instance.table)


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
            found = page_response.json()["found"]
            if page >= page_response.json()["pages"] - 1:
                break
            founded_vacancies += page_response.json()["items"]
        vacancies_salary = []
        for vacancy in founded_vacancies:
            rub_salary = predict_rub_salary_for_hh(vacancy)
            if rub_salary is not None:
                vacancies_salary.append(rub_salary)
        vacancies_stats[lang] = {"vacancies_found": found, "vacancies_processed": len(
            vacancies_salary), "average_salary": int(sum(vacancies_salary) / len(vacancies_salary))}

    print_stats_table(vacancies_stats, "HeadHuner Moscow")


def get_sj_vacancies():
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
        for vacancy in response.json()["objects"]:
            founded_vacancies.append(
                {"profession": vacancy['profession'], "salary": predict_rub_salary_for_sj(vacancy)})
        if response.json()["more"] != True:
            break

    vacancies_stats = {}
    for lang in POPULAR_PROGRAMMING_LANGS:
        vacancies_found = 0
        vacancies_salary = []
        for vacancy in founded_vacancies:
            if lang in vacancy["profession"]:
                vacancies_found += 1
                if vacancy["salary"] is not None:
                    vacancies_salary.append(vacancy["salary"])
        average_salary = int(sum(
            vacancies_salary) / len(vacancies_salary)) if len(vacancies_salary) > 0 else None
        vacancies_stats[lang] = {"vacancies_found": vacancies_found, "vacancies_processed": len(
            vacancies_salary), "average_salary": average_salary}

    print_stats_table(vacancies_stats, "SuperJob Moscow")


def main():
    load_dotenv()

    get_hh_vacancies()
    get_sj_vacancies()


if __name__ == "__main__":
    main()