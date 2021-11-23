"""
Скрипт для парсинга вакансий по поисковому запросу с сайта hh.ru
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

На данный момент все данные собираются в один длинный список, состоящий из словарей такого формата:
{'name': name, 'link': link, 'salary_from': salary_from, 'salary_to': salary_to, 'company_name': company_name,
 'link_to_company': link_to_company, 'responsibility': responsibility, 'requirement': requirement,
 'date': date, 'hh_id': hh_id, 'city': city, 'salary_in': salary_in,
 'required_experience': required_experience, 'employment_mode': employment_mode, 'schedule': schedule,
 'key_skills': key_skills}
(salary_in - "руб" или "USD")
(key_skills - список всех ключевых навыков (может быть пустым))
"""
import datetime
import locale
import time
import os
from bs4 import BeautifulSoup
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# from db_helper import db_helper


locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


def parse_vacancies_on_page(page):
    """функция для поверхностного парсинга всех вакансий на одной странице"""
    all_vacancies = []  # все вакансии на данной странице
    soup = BeautifulSoup(page, features="html.parser")
    vacancies_on_page = soup.find_all("div", {"class": "vacancy-serp-item"})

    # Списки с предварительными данными на этой странице
    vacancy_names = []
    vacancy_cities = []
    vacancy_hh_ids = []
    vacancy_links = []
    vacancy_salary_min = []
    vacancy_salary_max = []
    vacancy_company_names = []
    vacancy_company_links = []
    vacancy_responsibilities = []
    vacancy_requirements = []
    vacancy_dates = []
    vacancy_salary_in = []

    # Парсинг каждой вакансии отдельно
    for vacancy in vacancies_on_page:
        vacancy_info_text = vacancy.find("div", {"class": "vacancy-serp-item__info"})

        # Название вакансии
        name_block = vacancy_info_text.find("a", {"class": "bloko-link HH-LinkModifier"})
        if name_block is not None:
            name = name_block.text
        else:
            name = ""
        vacancy_names.append(name)

        # Ссылка на вакансию
        vacancy_link_block = vacancy_info_text.find("a", {"class": "bloko-link HH-LinkModifier"})
        if vacancy_link_block is not None:
            vacancy_link = vacancy_link_block.get("href")
        else:
            vacancy_link = ""
        vacancy_links.append(vacancy_link)

        # Id вакансии на сайте hh
        if len(vacancy_link) == 0:
            vacancy_hh_id = None
        else:
            try:
                vacancy_hh_id = vacancy_link.split('/')[4].split("?")[0]
            except IndexError:
                vacancy_hh_id = None

        vacancy_hh_ids.append(vacancy_hh_id)

        vacancy_salary_block = vacancy.find("div", {"class": "vacancy-serp-item__sidebar"})
        if vacancy_salary_block is not None:
            vacancy_salary = vacancy_salary_block.text
        else:
            vacancy_salary = ""

        # Заполнение зарплатных данных (может быть Null)
        salary_from = None
        salary_to = None
        if len(vacancy_salary) == 0:
            salary_from = None
            salary_to = None
        elif vacancy_salary.find("-") != -1:
            salary_from = vacancy_salary.split('-')[0].replace(u'\xa0', u'')
            salary_to = vacancy_salary.split('-')[1].split("руб")[0].split("USD")[0].replace(u'\xa0', u'')
        elif vacancy_salary.find("от") != -1:
            salary_from = vacancy_salary.split('от')[1].split("руб")[0].split("USD")[0].replace(u'\xa0', u'')
            salary_to = None
        elif vacancy_salary.find("до") != -1:
            salary_from = None
            salary_to = vacancy_salary.split('до')[1].split("руб")[0].split("USD")[0].replace(u'\xa0', u'')

        try:
            salary_from = int(salary_from)
        except:
            salary_from = None

        try:
            salary_to = int(salary_to)
        except:
            salary_to = None

        vacancy_salary_min.append(salary_from)
        vacancy_salary_max.append(salary_to)

        # В какой валюте зарплата (может быть Null)
        if vacancy_salary.find("руб") != -1:
            vacancy_salary_in.append("руб")
        elif vacancy_salary.find("USD") != -1:
            vacancy_salary_in.append("USD")
        else:
            vacancy_salary_in.append(None)

        # Название компании
        vacancy_company = vacancy.find("div", {"class": "vacancy-serp-item__meta-info"})
        if vacancy_company is not None:
            vacancy_company_name = vacancy_company.text.replace(u'\xa0', u'')
        else:
            vacancy_company_name = ""
        vacancy_company_names.append(vacancy_company_name)

        # Ссылка на компанию
        vacancy_company_link_block = vacancy_company.find("a", {"class": "bloko-link bloko-link_secondary"})
        if vacancy_company_link_block is not None:
            vacancy_company_link = "https://hh.ru" + vacancy_company_link_block.get('href')
        else:
            vacancy_company_link = ""
        vacancy_company_links.append(vacancy_company_link)

        # Город вакансии
        vacancy_city_block = vacancy.find("span", {"data-qa": "vacancy-serp__vacancy-address"})
        if vacancy_city_block is not None:
            vacancy_city = vacancy_city_block.text.split(',')[0]
        else:
            vacancy_city = ""
        vacancy_cities.append(vacancy_city)

        # Ответсвенность работника по данной вакансии
        vacancy_responsibility_block = vacancy.find("div", {"data-qa": "vacancy-serp__vacancy_snippet_responsibility"})
        if vacancy_responsibility_block is not None:
            vacancy_responsibility = vacancy_responsibility_block.text
        else:
            vacancy_responsibility = ""
        vacancy_responsibilities.append(vacancy_responsibility)

        # Требования для работника по данной вакансии
        vacancy_requirement_block = vacancy.find("div", {"data-qa": "vacancy-serp__vacancy_snippet_requirement"})
        if vacancy_requirement_block is not None:
            vacancy_requirement = vacancy_requirement_block.text
        else:
            vacancy_requirement = ""
        vacancy_requirements.append(vacancy_requirement)

        # Дата, когда была выложена вакансия
        vacancy_date_block = vacancy.find("span", {"class": "vacancy-serp-item__publication-date"})
        if vacancy_date_block is not None:
            vacancy_date_text = vacancy_date_block.text
        else:
            vacancy_date_text = ""

        if len(vacancy_date_text) == 0:
            vacancy_dates.append(None)
        else:
            vacancy_dates.append(parse_date(vacancy_date_text))

    # Заполнение словарей по каждой вакансии
    for i in range(len(vacancy_names)):
        vacancy = {"name": vacancy_names[i], "link": vacancy_links[i],
                   "salary_from": vacancy_salary_min[i], "salary_to": vacancy_salary_max[i],
                   "company_name": vacancy_company_names[i], "link_to_company": vacancy_company_links[i],
                   "responsibility": vacancy_responsibilities[i], "requirement": vacancy_requirements[i],
                   "date": vacancy_dates[i], "hh_id": vacancy_hh_ids[i], "city": vacancy_cities[i],
                   "salary_in": vacancy_salary_in[i]}
        all_vacancies.append(vacancy)
    return all_vacancies


def parse_vacancy(page):
    """функция парсинга одной вакансии со страницы этой вакансии"""
    key_skills = []

    soup = BeautifulSoup(page, features="html.parser")

    # Требуемый опыт работы
    required_experience_block = soup.find("span", {"data-qa": "vacancy-experience"})
    if required_experience_block is not None:
        required_experience = required_experience_block.text
    else:
        required_experience = ""

    employment_block = soup.find("p", {"data-qa": "vacancy-view-employment-mode"})

    # Тип занятости
    if employment_block is not None:
        employment_mode = employment_block.text.split(', ')[0]
    else:
        employment_mode = ""

    # График работы
    if employment_block is not None:
        schedule = employment_block.text.split(', ')[1]
    else:
        schedule = ""

    # Ключевые навыки
    all_skills = soup.find_all("span", {"class": "bloko-tag__section_text"})
    for skill in all_skills:
        key_skills.append(skill.text.replace(u'\xa0', u' '))

    # Доп. инфа с полного парсинга
    vacancy = {"required_experience": required_experience, "employment_mode": employment_mode,
               "schedule": schedule, "key_skills": key_skills}

    return vacancy


def check_exists_by_class_name(class_name, browser):
    """Проверяет наличие элемента на странице по имени класса"""
    try:
        browser.find_element_by_class_name(class_name)
    except NoSuchElementException:
        return False
    return True


def parse_date(date_str):
    """Парсит дату вакансии"""
    try:
        day = int(date_str.split("\xa0")[0])
        month_str = date_str.split("\xa0")[1]
        a = datetime.date.today()
        month_dict = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7, "августа": 8,
                      "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12}
        if month_str in month_dict.keys():
            month = month_dict[month_str]
        else:
            month = a.month
        year = a.year
        if month > a.month:
            year -= 1
        return datetime.date(year, month, day).isoformat()
    except IndexError:
        return None


def get_vacancies(query, region):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')  # Невидимый режим браузера
    options.add_argument('--log-level=1')  # Не выводит логи браузера в командную строку
    browser = webdriver.Remote(command_executor='http://selenium:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
    time.sleep(1)
    # Ввод поискового запроса по вакансиям
    vacancy_search = query

    # Первоначальные ссылки по регионам + добавление поискового запроса в URL
    kazan_hh_url = "https://kazan.hh.ru/search/vacancy?clusters=true&enable_snippets=true&items_on_page=100" \
                   "&no_magic=true&specialization=1&text="
    russia_hh_url = "https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&items_on_page=100&no_magic=true&specialization=1&text="
    tatarstan_hh_url = "https://kazan.hh.ru/search/vacancy?clusters=true&enable_snippets=true&items_on_page=100" \
                       "&no_magic=true&specialization=1&text="
    innopolis_hh_url = "https://innopolis.hh.ru/search/vacancy?clusters=true&enable_snippets=true&items_on_page=100" \
                       "&search_field=name&specialization=1&text="
    kazan_hh_url += quote(vacancy_search)
    russia_hh_url += quote(vacancy_search)
    tatarstan_hh_url += quote(vacancy_search)
    innopolis_hh_url += quote(vacancy_search)
    tatarstan_hh_url += "&L_save_area=true&area=1624&from=cluster_area&showClusters=false"
    russia_hh_url += "&L_save_area=true&area=113&from=cluster_area&showClusters=true"
    kazan_hh_url += "&L_save_area=true&area=88&from=cluster_area&showClusters=true"
    innopolis_hh_url += "&L_save_area=true&area=2734&from=cluster_area&showClusters=true"

    all_vacancies = []  # все вакансии по данному поисковому запросу в данном регионе

    regions = {
        1: russia_hh_url,
        2: tatarstan_hh_url,
        3: kazan_hh_url,
        4: innopolis_hh_url}
    # Выбор региона поиска
    if region in regions.keys():
        browser.get(regions[region])
    else:
        browser.get("http://google.com")
    print(regions[region])

    page = browser.page_source
    while check_exists_by_class_name("HH-Pager-Controls-Next", browser):
        all_vacancies += parse_vacancies_on_page(page)
        browser.find_element_by_class_name("HH-Pager-Controls-Next").click()
        page = browser.page_source
    all_vacancies += parse_vacancies_on_page(page)

    i = int(0)
    for vacancy in all_vacancies:
        vacancy_link = vacancy["link"]
        browser.get(vacancy_link)
        page = browser.page_source
        # Добавляем доп. данные в словарь текущей вакансии
        all_vacancies[i].update(parse_vacancy(page))
        all_vacancies[i].update(region=region, query=query)
        i += 1
    browser.close()
    return all_vacancies


if __name__ == "__main__":
    query = input("Введите вакансию для парсинга: ")
    region = int(input("Введите регион, по которому будет произведен парсинг (1-Россия, 2-Татарстан, 3-Казань,"
                            " 4-Иннополис, все остальное ничего не делает): "))
    table_name = get_vacancies(query, region)
