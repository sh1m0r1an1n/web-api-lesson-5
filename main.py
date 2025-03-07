import requests
from environs import Env
from terminaltables import AsciiTable


def get_hh_salary(vacancy):
    salary_data = vacancy.get("salary")
    if not salary_data or salary_data.get("currency") != "RUR":
        return None, None
    return salary_data.get("from"), salary_data.get("to")


def get_sj_salary(vacancy):
    if vacancy.get("currency") != "rub":
        return None, None
    return vacancy.get("payment_from"), vacancy.get("payment_to")


def predict_rub_salary(salary_from, salary_to):
    """Рассчитывает зарплату исходя из зарплатной вилки"""
    if salary_from and salary_to:
        return (salary_from + salary_to) // 2
    elif salary_from:
        return int(salary_from * 1.2)
    elif salary_to:
        return int(salary_to * 0.8)
    return None


def download_all_pages_of_the_sj_request(url, headers, params):
    all_vacancies = []

    while True:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            response = response.json()
        except requests.exceptions.RequestException as error:
            print(f"Ошибка при отправке запроса sj: {error}")
            continue

        all_vacancies.extend(response.get("objects", []))

        if not response.get("more", False):
            break

        params["page"] += 1

    count, vacancies = response.get("total", 0), all_vacancies

    return count, vacancies


def get_sj_vacancies(language, token):
    """Получение вакансий с SuperJob"""
    url = f"https://api.superjob.ru/2.0/vacancies/"
    search_text = f'"{language}"' if language != "C" \
        else '!"C" NOT "C++" NOT "C#" NOT "Objective-C" NOT "1C"'
    headers = {"X-Api-App-Id": token}

    programmer_and_developer_id = 48
    moscow_id = 4
    days = 30
    params = {
        "period": days,
        "town": moscow_id,
        "keyword": search_text,
        "catalogues": programmer_and_developer_id,
        "count": 100,
        "page": 0,
    }
    count, vacancies = download_all_pages_of_the_sj_request(url, headers, params)
    return count, vacancies


def download_all_pages_of_the_hh_request(url, params):
    all_vacancies = []

    while True:
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            response = response.json()
        except requests.exceptions.RequestException as error:
            print(f"Ошибка при отправке запроса hh: {error}")
            continue

        all_vacancies.extend(response.get("items", []))

        if params["page"] >= response.get("pages", 1) - 1:
            break

        params["page"] += 1

    count, vacancies = response.get("found", 0), all_vacancies

    return count, vacancies


def get_hh_vacancies(language):
    """Получение вакансий с HeadHunter"""
    url = "https://api.hh.ru/vacancies"
    search_text = f'"{language}"' if language != "C"\
        else '!"C" NOT "C++" NOT "C#" NOT "Objective-C" NOT "1C"'

    programmer_and_developer_id = 96
    moscow_id = 1
    days = 30
    params = {
        "professional_role": programmer_and_developer_id,
        "area": moscow_id,
        "currency": "RUR",
        "period": days,
        "text": search_text,
        "per_page": 100,
        "page": 0,
    }
    count, vacancies = download_all_pages_of_the_hh_request(url, params)
    return count, vacancies


def create_table(statistics_on_vacancies, title):
    """Отображение вакансий в виде таблицы"""
    table_data = [[
        "Язык программирования",
        "Вакансий найдено",
        "Вакансий обработано",
        "Средняя зарплата"
    ]]

    for language, statistics in statistics_on_vacancies.items():
        table_data.append([
            language,
            str(statistics["vacancies_found"]),
            str(statistics["vacancies_processed"]),
            str(statistics["average_salary"])
        ])
    table = AsciiTable(table_data)
    table.title = title
    return table.table


def get_hh_statistics_on_vacancies(languages):
    """Статистика по вакансиям и языкам для HeadHunter"""
    statistics = {}

    for lang in languages:
        count, vacancies = get_hh_vacancies(lang)

        salaries = []
        for vacancy in vacancies:
            salary_from, salary_to = get_hh_salary(vacancy)
            salary = predict_rub_salary(salary_from, salary_to)
            if salary:
                salaries.append(salary)

        average_salary = int(sum(salaries) / len(salaries)) if salaries else 0

        statistics[lang] = {
            "vacancies_found": count,
            "vacancies_processed": len(salaries),
            "average_salary": average_salary,
        }
    return statistics


def get_sj_statistics_on_vacancies(languages, sj_token):
    """Статистика по вакансиям и языкам для SuperJob"""
    statistics = {}

    for lang in languages:
        count, vacancies = get_sj_vacancies(lang, sj_token)

        salaries = []
        for vacancy in vacancies:
            salary_from, salary_to = get_sj_salary(vacancy)
            salary = predict_rub_salary(salary_from, salary_to)
            if salary:
                salaries.append(salary)

        average_salary = int(sum(salaries) / len(salaries)) if salaries else 0

        statistics[lang] = {
            "vacancies_found": count,
            "vacancies_processed": len(salaries),
            "average_salary": average_salary,
        }
    return statistics


def main():
    env = Env()
    env.read_env()

    languages = [
        "JavaScript",
        "Java",
        "Python",
        "Ruby",
        "PHP",
        "C++",
        "C#",
        "C",
        "Go",
        "Objective-C",
        "Scala",
        "Swift",
        "TypeScript",
        "1С"
    ]
    sj_token = env.str("SECRET_KEY_SUPERJOB", "")

    hh_msc = get_hh_statistics_on_vacancies(languages)

    if sj_token:
        sj_msc = get_sj_statistics_on_vacancies(languages, sj_token)
    else:
        sj_msc = {}
        print("Токен SuperJob не найден. Статистика по SJ пропущена.")

    print(create_table(hh_msc, title="HeadHunter Moscow"))
    print("\n" + create_table(sj_msc, title="SuperJob Moscow"))


if __name__ == "__main__":
    main()
