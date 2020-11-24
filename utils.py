import datetime as dt
from terminaltables import AsciiTable


POPULAR_PROGRAMMING_LANGS = ["JavaScript",
                             "Java", "Python", "Ruby", "PHP", "C++", "C#", "C", "Go"]


def predict_rub_salary(salary_from, salary_to):
    if (not salary_from) | (salary_from == 0):
        return int(salary_to * 0.8)
    elif (not salary_to) | (salary_to == 0):
        return int(salary_from * 1.2)
    elif salary_from & salary_to:
        return int((salary_from + salary_to) / 2)
    else:
        return None


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
