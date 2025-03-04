import requests
from environs import Env
from terminaltables import AsciiTable


def predict_rub_salary(vacancy, platform):
    """Универсальная функция для расчета зарплаты"""
    if platform == "hh":
        salary_data = vacancy.get("salary")
        if not salary_data or salary_data.get("currency") != "RUR":
            return None
        salary_from = salary_data.get("from")
        salary_to = salary_data.get("to")
    elif platform == "sj":
        if vacancy["currency"] != "rub":
            return None
        salary_from = vacancy.get("payment_from")
        salary_to = vacancy.get("payment_to")
    else:
        return None

    if salary_from and salary_to:
        return (salary_from + salary_to) // 2
    elif salary_from:
        return int(salary_from * 1.2)
    elif salary_to:
        return int(salary_to * 0.8)
    return None


def get_sj_vacancies(token, language):
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

    all_vacancies = []

    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        all_vacancies.extend(data.get("objects", []))

        if not data.get("more", False):
            break

        params["page"] += 1

    return data.get("total", 0), all_vacancies


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

    all_vacancies = []

    while True:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        all_vacancies.extend(data.get("items", []))

        if params["page"] >= data.get("pages", 1) - 1:
            break

        params["page"] += 1

    return data.get("found", 0), all_vacancies


def create_table(results, title):
    """Отображение вакансий в виде таблицы"""
    table_data = [[
        "Язык программирования",
        "Вакансий найдено",
        "Вакансий обработано",
        "Средняя зарплата"
    ]]

    for key, value in results.items():
        table_data.append([
            key,
            str(value["vacancies_found"]),
            str(value["vacancies_processed"]),
            str(value["average_salary"])
        ])
    table = AsciiTable(table_data)
    table.title = title
    return table.table


def get_language_statistics(lang, sj_token=None):
    """Статистика по вакансиям по одному языку на платформе"""
    if sj_token:
        count, vacancies = get_sj_vacancies(sj_token, lang)
    else:
        count, vacancies = get_hh_vacancies(lang)
    return count, vacancies


def get_statistics_on_vacancies(languages, platform, sj_token=None):
    """Статистика по вакансиям и языкам на платформе"""
    statistics = {}

    for lang in languages:
        count, vacancies = get_language_statistics(lang, sj_token)

        salaries = []
        for vacancy in vacancies:
            salary = predict_rub_salary(vacancy, platform)
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

    hh_msc = get_statistics_on_vacancies(languages=languages, platform="hh")

    sj_msc = {}
    if sj_token:
        sj_msc = get_statistics_on_vacancies(
            languages=languages, platform="sj", sj_token=sj_token
        )
    else:
        print("Токен SuperJob не найден. Статистика по SJ пропущена.")

    print(create_table(hh_msc, title="HeadHunter Moscow"))
    print("\n" + create_table(sj_msc, title="SuperJob Moscow"))


if __name__ == "__main__":
    main()
