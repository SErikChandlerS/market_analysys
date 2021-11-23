from tkinter import *
import webbrowser
# #GUI
# first_window = Tk()
# first_window.title("Market analysis")
# first_window.geometry("1280x720")

def VACpar(vacancy, reg):
    import datetime
    import locale

    from bs4 import BeautifulSoup
    from urllib.parse import quote
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager

    # from db_helper import db_helper

    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    options = webdriver.ChromeOptions()
    options.add_argument('headless')  # Невидимый режим браузера
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    wait = WebDriverWait(browser, 1000)

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
            if len(vacancy_salary) == 0:
                vacancy_salary_min.append(None)
                vacancy_salary_max.append(None)
            elif vacancy_salary.find("-") != -1:
                vacancy_salary_min.append(vacancy_salary.split('-')[0].replace(u'\xa0', u''))
                vacancy_salary_max.append(
                    vacancy_salary.split('-')[1].split("руб")[0].split("USD")[0].replace(u'\xa0', u''))
            elif vacancy_salary.find("от") != -1:
                vacancy_salary_min.append(
                    vacancy_salary.split('от')[1].split("руб")[0].split("USD")[0].replace(u'\xa0', u''))
                vacancy_salary_max.append(None)
            elif vacancy_salary.find("до") != -1:
                vacancy_salary_min.append(None)
                vacancy_salary_max.append(
                    vacancy_salary.split('до')[1].split("руб")[0].split("USD")[0].replace(u'\xa0', u''))

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
            vacancy_responsibility_block = vacancy.find("div",
                                                        {"data-qa": "vacancy-serp__vacancy_snippet_responsibility"})
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

    def check_exists_by_class_name(class_name):
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
            month_dict = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7,
                          "августа": 8,
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
        # Ввод поискового запроса по вакансиям
        vacancy_search = query

        # Первоначальные ссылки по регионам + добавление поискового запроса в URL
        kazan_hh_url = "https://kazan.hh.ru/search/vacancy?clusters=true&enable_snippets=true&items_on_page=100" \
                       "&no_magic=true&text="
        russia_hh_url = "https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&items_on_page=100&no_magic=true&text="
        tatarstan_hh_url = "https://kazan.hh.ru/search/vacancy?clusters=true&enable_snippets=true&items_on_page=100" \
                           "&no_magic=true&text="
        innopolis_hh_url = "https://innopolis.hh.ru/search/vacancy?clusters=true&enable_snippets=true&items_on_page=100" \
                           "&search_field=name&text="
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

        page = browser.page_source
        while check_exists_by_class_name("HH-Pager-Controls-Next"):
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
        return all_vacancies

    if __name__ == "__main__":
        query = vacancy
        region = reg
        table_name = get_vacancies(query, region)


def CVpar2(link, parsingmode):
    import datetime
    import locale

    from selenium import webdriver
    from bs4 import BeautifulSoup
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager

    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    options = webdriver.ChromeOptions()
    options.add_argument('headless')  # Невидимый режим браузера
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    wait = WebDriverWait(browser, 1000)

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
            resume_name = resume.find("a", {"class": "resume-search-item__name"}).text
            resume_names.append(resume_name)

            # Id резюме на сайте hh.ru
            resume_id = resume.get("data-resume-id")
            resume_ids.append(resume_id)

            # Ссылка на резюме на сайте hh.ru
            resume_link = "https://hh.ru" + resume.find("a", {"class": "resume-search-item__name"}).get("href")
            resume_links.append(resume_link)

            # Возраст владельца резюме
            resume_age = resume.find("span", {"data-qa": "resume-serp__resume-age"})
            if resume_age is not None:
                resume_age = resume_age.text.split('\xa0')[0]
            resume_ages.append(resume_age)

            # Зарплата и валюта, в которой указана зарплата
            resume_salary = resume.find("div", {"class": "resume-search-item__compensation"}).text
            if resume_salary.find("руб") != -1:
                salary_in = "руб"
            elif resume_salary.find("USD") != -1:
                salary_in = "USD"
            else:
                salary_in = None
            resume_salary = resume_salary.replace(u'\u2009', u'').replace(u'\xa0', u' ').split(' ')[0]
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
            resume_last_works.append(resume_last_work)

        # Заполнение словарей по каждому резюме
        for i in range(len(resume_names)):
            CV = {"name": resume_names[i], "link": resume_links[i], "id": resume_ids[i], "age": resume_ages[i],
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
        sex = soup.find("span", {"data-qa": "resume-personal-gender"}).text

        # Город владельца резюме
        city = soup.find("span", {"data-qa": "resume-personal-address"}).text

        resume_block = soup.find("div", {"class": "resume-block", "data-qa": "resume-block-position"})

        if resume_block is not None:
            # Категория специализации
            specialization_category = resume_block.find("span",
                                                        {"data-qa": "resume-block-specialization-category"}).text

            # Специализации
            for specialization in resume_block.find_all("li", {"data-qa": "resume-block-position-specialization"}):
                specializations.append(specialization.text)

            employment_block = resume_block.find_all("p")

            # Типы занятости
            employment_modes = employment_block[0].text.split(": ")[1].split(', ')

            # Графики работы
            schedule = employment_block[1].text.split(": ")[1].split(', ')

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
                previous_positions[i].update({"position": pos.text})
                i += 1

        # Ключевые навыки
        all_skills = soup.find_all("span", {"class": "bloko-tag__section_text"})
        for skill in all_skills:
            key_skills.append(skill.text.replace(u'\xa0', u' '))

        # Образование владельца резюме
        education_block = soup.find("div", {"data-qa": "resume-block-education"})
        if education_block is not None:
            education = education_block.find("span", {"class": "resume-block__title-text_sub"}).text

        # Языки владельца резюме
        all_languages = soup.find_all("p", {"data-qa": "resume-block-language-item"})
        for language in all_languages:
            languages.append(language.text)

        # Заполнение словаря резюме
        CV = {"sex": sex, "city": city, "specialization_category": specialization_category,
              "specializations": specializations, "employment_modes": employment_modes, "schedule": schedule,
              "previous_positions": previous_positions, "key_skills": key_skills, "education": education,
              "languages": languages}
        return CV

    def check_exists_by_class_name(class_name):
        """Проверяет наличие элемента на странице по имени класса"""
        try:
            browser.find_element_by_class_name(class_name)
        except NoSuchElementException:
            return False
        return True

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

    def check_exists_by_link_text(link_text):
        """Проверяет наличие элемента на странице по тексту ссылки"""
        try:
            browser.find_element_by_link_text(link_text)
        except NoSuchElementException:
            return False
        return True

    if __name__ == "__main__":
        # Ссылка на chromedriver, для замены надо скачать другой драйвер и добавить в папку drivers

        all_CVs = []  # все резюме по данному поисковому запросу в данном регионе

        # Получение ссылки на hh.ru со всеми выбранными параметрами поиска
        start_link = link

        # Выбор режима парсинга
        checkParseMode = parsingmode

        browser.get(start_link)

        # Поверхностный парсинг каждой страницы и получение данных
        if checkParseMode == 1 or checkParseMode == 2:
            page = browser.page_source
            while check_exists_by_link_text("дальше"):
                all_CVs += parse_resumes_on_page(page)
                browser.find_element_by_link_text("дальше").click()
                page = browser.page_source
            all_CVs += parse_resumes_on_page(page)

        # Полный парсинг, если выбран режим полного парсинга
        # (Уже до этого можно использовать предварительный (без доп. инфы) список all_CVs, если надо)
        if checkParseMode == 2:
            i = int(0)
            for CV in all_CVs:
                cv_link = CV['link']
                browser.get(cv_link)
                page = browser.page_source
                # Добавляем доп. данные в словарь текущего резюме
                all_CVs[i].update(parse_resume(page))
                i += 1

        # Вывод всех данных и общего числа найденных резюме (можно закомментить)
        for CV in all_CVs:
            print(CV)
        print("Получено " + str(len(all_CVs)) + " Резюме")








#Defining parsing code or import it
def execute():
    pass

def cancel():
    exit("End")




def Mainwindow():
    # GUI


    first_window = Tk()
    first_window.resizable(False, False)
    first_window.title("Market analysis")
    first_window.geometry("1280x720")

    # Frame
    First_frame = Frame(first_window)
    First_frame.place(x=530, y=330)

    # Labels:
    label = Label(first_window, text="Провести анализ рынка?").place(x=550, y=230)

    def change():
        if var.get() == 0:
            first_window.destroy()
            CVwindow()
        elif var.get() == 1:
            first_window.destroy()
            Vacancywindow()


    # Buttons:
    var = IntVar()
    var.set(0)
    CV = Radiobutton(text="Резюме", variable=var, value=0).place(x=600, y=270)
    Vacancy = Radiobutton(text="Вакансии", variable=var, value=1).place(x=600, y=290)

    b = Button(First_frame, text="Выбрать", width=12, command=change).grid(row=0, column=0)
    Button(First_frame, text="Отмена", width=12, command=cancel).grid(row=0, column=1)

    def callback(event):
        webbrowser.open_new(event.widget.cget("text"))
    lbl = Label(first_window, text=r"http://www.hh.ru", fg="blue", cursor="hand2")
    lbl.place(x=580, y=700)
    lbl.bind("<Button-1>", callback)

    first_window.mainloop()


def OUTPUTwindow(text):
    window = Tk()
    window.geometry("1280x720")
    window.resizable(False, False)
    window.title("Результат")
    def back():
        window.destroy()
        Mainwindow()

    Label(window,text=text).place(x=10, y=10)
    Button(window, text="Назад", width=12, command=back).place(x=580, y=700)


def CVwindow():
    first = Tk()
    first.resizable(False, False)
    first.title("Меню резюме")

    def back():
        first.destroy()
        Mainwindow()


    first.geometry("1280x720")
    Label(first, text="1. Введите ссылку с поиском по резюме и всеми нужными \n вам параметрами поиска (лучше 100 резюме на странице):").place(x=430, y=130)

    link = StringVar()

    e1 = Entry(textvariable=link,width=50).place(x=430, y=180)

    # e1 = Text(first, width=20, height=5, background="light grey").grid(row=3, column=1)
    def insert():
        print(link.get())
    # Button(first, text="Вставить", command=insert).place(x=580, y=230)
    Label(first, text="2. Выберите режим парсинга (Поверхностный, Полный): ").place(x=430, y=300)

    def change():
        out = CVpar2(link.get(),var.get())
        outtext = ""
        for cv in out:
            outtext += "\n" + str(cv)
            print(outtext)
        first.destroy()
        OUTPUTwindow(outtext)





    # Buttons:
    var = IntVar()
    var.set(1)
    CV = Radiobutton(text="Поверхностный", variable=var, value=1).place(x=550, y=340)
    Vacancy = Radiobutton(text="Полный", variable=var, value=2).place(x=550, y=370)



    # Button(first, text="Вставить", command=insert).grid(row=4, column=1)
    First_frame = Frame(first)
    First_frame.place(x=500, y=420)

    Button(First_frame, text="Анализировать", width=12, command=change).grid(row=0, column=0)
    Button(First_frame, text="Назад", width=12, command=back).grid(row=0, column=1)

    def callback(event):
        webbrowser.open_new(event.widget.cget("text"))
    lbl = Label(first, text=r"http://www.hh.ru", fg="blue", cursor="hand2")
    lbl.place(x=580, y=700)
    lbl.bind("<Button-1>", callback)

    first.mainloop()

def Vacancywindow():
    second = Tk()
    second.resizable(False, False)
    second.title("Меню вакансий")

    def back():
        second.destroy()
        Mainwindow()

    second.geometry("1280x720")
    Label(second,
          text="1. Введите вакансию для парсинга:").place(
        x=430, y=130)

    vacancy = StringVar()

    e1 = Entry(textvariable=vacancy, width=50).place(x=430, y=180)

    def insert():
        print(vacancy.get())

    # Button(first, text="Вставить", command=insert).place(x=580, y=230)
    Label(second, text="2. Выберите регион, по которому будет произведен парсинг: ").place(x=430, y=300)

    def change():
        # out = VACpar(vacancy.get(), var.get())
        # outtext = ""
        # for cv in out:
        #     outtext += "\n" + str(cv)
        #     print(outtext)
        # second.destroy()
        # OUTPUTwindow(outtext)
        pass

    # Buttons:
    var = IntVar()
    var.set(1)
    Radiobutton(text="Россия", variable=var, value=1).place(x=550, y=340)
    Radiobutton(text="Татарстан", variable=var, value=2).place(x=550, y=370)
    Radiobutton(text="Казань", variable=var, value=3).place(x=550, y=400)
    Radiobutton(text="Иннополис", variable=var, value=4).place(x=550, y=430)

    # Button(first, text="Вставить", command=insert).grid(row=4, column=1)
    First_frame = Frame(second)
    First_frame.place(x=500, y=470)

    Button(First_frame, text="Анализировать", width=12, command=change).grid(row=0, column=0)
    Button(First_frame, text="Назад", width=12, command=back).grid(row=0, column=1)

    def callback(event):
        webbrowser.open_new(event.widget.cget("text"))

    lbl = Label(second, text=r"http://www.hh.ru", fg="blue", cursor="hand2")
    lbl.place(x=580, y=700)
    lbl.bind("<Button-1>", callback)

    second.mainloop()

# #Frame
# First_frame = Frame(first_window)
# First_frame.grid(row=3, column=1)
#
# #Labels:
# label = Label(first_window, text="Провести анализ рынка?").grid(row=0, column=1)
#
# #Buttons:
# var = IntVar()
# var.set(0)
# CV = Radiobutton(text="Резюме", variable=var, value=0).grid(row=1, column=1)
# Vacancy = Radiobutton(text="Вакансии", variable=var, value=1).grid(row=2, column=1)
#
# b = Button(First_frame, text="Выбрать", width=12, command=change).grid(row=0, column=0)
# Button(First_frame, text="Отмена", width=12, command=cancel).grid(row=0, column=1)

#Input
# inputBox = Entry(first_window, width=20, bg="light grey")
# inputBox.grid(row=1, column=1)




#Output


#start
if __name__ == '__main__':
    Mainwindow()




