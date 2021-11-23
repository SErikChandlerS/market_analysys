"""
Скрипт для парсинга резюме с сайта hh.ru
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

На данный момент все данные собираются в один длинный список, состоящий из словарей такого формата:
{"name": name, "link": link, "id": id, "age": age, "salary": salary, "salary_in": salary_in,
 "experience_years": years, "experience_months": months, "last_work": last_work}
(salary_in - "руб" или "USD")

При парсинге в полном режиме ко всему выше добавляются также:
{"sex": sex, "city": city, "specialization_category": specialization_category,
 "specializations": specializations, "employment_modes": employment_modes, "schedule": schedule,
 "previous_positions": previous_positions, "key_skills": key_skills, "education": education,
 "languages": languages}
(specializations - список всех специализаций (может быть пустым),
 employment_modes - список всех типов занятости (может быть пустым),
 schedule - список всех возможных графиков работы (может быть пустым),
 previous_positions - список всех позиций, на которых работал владелец резюме, состоящий из словарей такого типа:
 {"years": years, "months": months, "position": position} (может быть пустым),
 key_skills - список всех ключевых навыков (может быть пустым),
 languages - список всех языков с уровнем владения (может быть пустым))
"""
import datetime
import locale
import time
import os

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib.parse import quote


locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


def parse_resumes_on_page(page):
    """функция для поверхностного парсинга всех резюме на одной странице"""
    all_resumes = []  # Все резюме на данной странице
    soup = BeautifulSoup(page, features="html.parser")
    all_resume_on_page = soup.find_all("div", {"class": "resume-search-item"})

    # Списки с предварительными данными на этой странице
    resume_names = []
    resume_ids = []
    resume_links = []
    resume_ages = []
    resume_salaries = []
    resume_salaries_in = []
    resume_experiences_years = []
    resume_experiences_months = []
    resume_last_works = []

    # Парсинг каждого резюме отдельно
    for resume in all_resume_on_page:
        # Название резюме
        resume_name_block = resume.find("a", {"class": "resume-search-item__name"})
        if resume_name_block is not None:
            resume_name = resume_name_block.text
        else:
            resume_name = ""
        resume_names.append(resume_name)

        # Id резюме на сайте hh.ru
        resume_id = resume.get("data-resume-id")
        resume_ids.append(resume_id)

        # Ссылка на резюме на сайте hh.ru
        resume_link_block = resume.find("a", {"class": "resume-search-item__name"})
        if resume_link_block is not None:
            resume_link = "https://hh.ru" + resume_link_block.get("href")
        else:
            resume_link = ""
        resume_links.append(resume_link)

        # Возраст владельца резюме
        resume_age = resume.find("span", {"data-qa": "resume-serp__resume-age"})
        if resume_age is not None:
            resume_age = resume_age.text.split('\xa0')[0]
        else:
            resume_age = None
        resume_ages.append(resume_age)

        # Зарплата и валюта, в которой указана зарплата
        resume_salary_block = resume.find("div", {"class": "resume-search-item__compensation"})

        if resume_salary_block is not None:
            resume_salary = resume_salary_block.text
        else:
            resume_salary = ""

        if resume_salary.find("руб") != -1:
            salary_in = "руб"
        elif resume_salary.find("USD") != -1:
            salary_in = "USD"
        else:
            salary_in = None

        try:
            resume_salary = int(resume_salary.replace(u'\u2009', u'').replace(u'\xa0', u' ').split(' ')[0])
        except:
            resume_salary = None
            pass
        resume_salaries.append(resume_salary)
        resume_salaries_in.append(salary_in)

        # Опыт работы в годах и месяцах
        resume_experience = resume.find("div", {"data-qa": "resume-serp__resume-excpirience-sum"})
        exp = parse_experience(resume_experience)
        experience_years = exp[0]
        resume_experiences_years.append(experience_years)
        experience_months = exp[1]
        resume_experiences_months.append(experience_months)

        # Информация о прошлой работе
        resume_last_work = resume.find("span", {"class": "bloko-link-switch_inherited"})
        if resume_last_work is not None:
            resume_last_work = resume_last_work.text
        else:
            resume_last_work = ""
        resume_last_works.append(resume_last_work)

    # Заполнение словарей по каждому резюме
    for i in range(len(resume_names)):
        CV = {"name": resume_names[i], "link": resume_links[i], "hh_id": resume_ids[i], "age": resume_ages[i],
              "salary": resume_salaries[i], "salary_in": resume_salaries_in[i],
              "experience_years": resume_experiences_years[i], "experience_months": resume_experiences_months[i],
              "last_work": resume_last_works[i]}
        all_resumes.append(CV)
    return all_resumes


def parse_resume(page):
    """функция парсинга одного резюме со страницы этого резюме"""

    # Списки и переменные с предварительными данными на этой странице
    specializations = []
    previous_positions = []
    key_skills = []
    languages = []
    employment_modes = []
    schedule = []
    education = None
    specialization_category = None

    soup = BeautifulSoup(page, features="html.parser")

    # Пол владельца резюме
    sex_block = soup.find("span", {"data-qa": "resume-personal-gender"})
    if sex_block is not None:
        sex = sex_block.text
    else:
        sex = ""

    # Город владельца резюме
    city_block = soup.find("span", {"data-qa": "resume-personal-address"})
    if city_block is not None:
        city = city_block.text
    else:
        city = ""

    resume_block = soup.find("div", {"class": "resume-block", "data-qa": "resume-block-position"})

    if resume_block is not None:
        # Категория специализации
        specialization_category_block = resume_block.find("span", {"data-qa": "resume-block-specialization-category"})
        if specialization_category_block is not None:
            specialization_category = specialization_category_block.text
        else:
            specialization_category = ""

        # Специализации
        for specialization in resume_block.find_all("li", {"data-qa": "resume-block-position-specialization"}):
            if specialization is not None:
                specializations.append(specialization.text)

        employment_block = resume_block.find_all("p")

        # Типы занятости
        try:
            employment_modes = employment_block[0].text.split(": ")[1].split(', ')
        except:
            employment_modes = []
        # Графики работы
        try:
            schedule = employment_block[1].text.split(": ")[1].split(', ')
        except:
            schedule = []

    resume_block_experience = soup.find("div", {"class": "resume-block", "data-qa": "resume-block-experience"})

    # Весь предыдущий опыт работы владельца резюме
    if resume_block_experience is not None:
        all_experience = resume_block_experience.find_all("div", {"class": "resume-block__experience-timeinterval"})

        for exp in all_experience:
            tmp = parse_experience(exp)
            months = tmp[1]
            years = tmp[0]
            position = {"years": years, "months": months}
            previous_positions.append(position)

        positions = resume_block_experience.find_all("div", {"class": "resume-block__sub-title",
                                                             "data-qa": "resume-block-experience-position"})
        i = 0
        for pos in positions:
            if pos is not None:
                previous_positions[i].update({"position": pos.text})
            else:
                previous_positions[i].update({"position": ""})
            i += 1

    # Ключевые навыки
    all_skills = soup.find_all("span", {"class": "bloko-tag__section_text"})
    for skill in all_skills:
        if skill is not None:
            key_skills.append(skill.text.replace(u'\xa0', u' '))

    # Образование владельца резюме
    education_block = soup.find("div", {"data-qa": "resume-block-education"})
    if education_block is not None:
        education = education_block.find("span", {"class": "resume-block__title-text_sub"})
        if education is not None:
            education = education.text

    # Языки владельца резюме
    all_languages = soup.find_all("p", {"data-qa": "resume-block-language-item"})
    for language in all_languages:
        if language is not None:
            languages.append(language.text)

    # Заполнение словаря резюме
    CV = {"sex": sex, "city": city, "specialization_category": specialization_category,
          "specializations": specializations, "employment_modes": employment_modes, "schedule": schedule,
          "previous_positions": previous_positions, "key_skills": key_skills, "education": education,
          "languages": languages}
    return CV


def parse_experience(resume_experience):
    """функция парсит текст опыта в годы и месяцы"""
    if resume_experience is not None:
        resume_experience = resume_experience.text
        resume_experience = resume_experience.split(' ')
        if len(resume_experience) == 1:
            if resume_experience[0].find("год") != -1 or resume_experience[0].find("лет") != -1:
                experience_years = resume_experience[0].split(u'\xa0')[0]
                experience_months = 0
            else:
                experience_years = 0
                experience_months = resume_experience[0].split(u'\xa0')[0]
        elif len(resume_experience) == 2:
            experience_years = resume_experience[0].split(u'\xa0')[0]
            experience_months = resume_experience[1].split(u'\xa0')[0]
        else:
            experience_years = 0
            experience_months = 0
    else:
        experience_years = 0
        experience_months = 0
    return [experience_years, experience_months]


def check_exists_by_link_text(link_text, browser):
    """Проверяет наличие элемента на странице по тексту ссылки"""
    try:
        browser.find_element_by_link_text(link_text)
    except NoSuchElementException:
        return False
    return True


def get_cvs(query, region):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')  # Невидимый режим браузера
    options.add_argument('--log-level=1')  # Не выводит логи браузера в командную строку
    browser = webdriver.Remote(command_executor='http://selenium:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
    time.sleep(1)
    # Ссылка на chromedriver, для замены надо скачать другой драйвер и добавить в папку drivers
    all_CVs = []  # все резюме по данному поисковому запросу в данном регионе
    vacancy_search = query
    # Первоначальные ссылки по регионам + добавление поискового запроса в URL
    kazan_hh_url = "https://kazan.hh.ru/search/resume?area=88&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&st=resumeSearch&items_on_page=100&text=%s&specialization=1&fromSearch=true" % quote(vacancy_search)
    russia_hh_url = "https://hh.ru/search/resume?area=113&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&st=resumeSearch&items_on_page=100&text=%s&specialization=1&fromSearch=true" % quote(vacancy_search)
    tatarstan_hh_url = "https://kazan.hh.ru/search/resume?area=1624&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&st=resumeSearch&items_on_page=100&text=%s&specialization=1&fromSearch=true" % quote(vacancy_search)
    innopolis_hh_url = "https://innopolis.hh.ru/search/resume?area=2734&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&st=resumeSearch&items_on_page=100&text=%s&specialization=1&fromSearch=true" % quote(vacancy_search)

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
    # browser.get(start_link)
    print(regions[region])
    # Поверхностный парсинг каждой страницы и получение данных
    page = browser.page_source
    while check_exists_by_link_text("дальше", browser):
        all_CVs += parse_resumes_on_page(page)
        browser.find_element_by_link_text("дальше").click()
        page = browser.page_source
    all_CVs += parse_resumes_on_page(page)

    i = int(0)
    for CV in all_CVs:
        cv_link = CV['link']
        browser.get(cv_link)
        page = browser.page_source
        # Добавляем доп. данные в словарь текущего резюме
        all_CVs[i].update(parse_resume(page))
        all_CVs[i].update(region=region, query=query)
        i += 1

    # Вывод всех данных и общего числа найденных резюме (можно закомментить)
    browser.close()
    return all_CVs


if __name__ == "__main__":
    query = input("Введите вакансию для парсинга: ")
    region = int(input("Введите регион, по которому будет произведен парсинг (1-Россия, 2-Татарстан, 3-Казань,"
                            " 4-Иннополис, все остальное ничего не делает): "))
    table_name = get_cvs(query, region)
