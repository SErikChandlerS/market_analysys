import pandas as pd


def get_vacancy_statistics(df: pd.DataFrame):
    sum = df.sum(axis = 0, skipna = True, numeric_only = True)
    num = df.count(axis = 0, numeric_only = True)
    stats = {}
    if ('salary_from' in sum) and ('salary_from' in num):
        if num['salary_from'] > 0:
            avr_from = sum['salary_from'] / num['salary_from']
            stats['vacancy_average_from'] = avr_from
    if ('salary_to' in sum) and ('salary_to' in num):
        if num['salary_to'] > 0:
            avr_to = sum['salary_to'] / num['salary_to']
            stats['vacancy_average_to'] = avr_to
    if ('required_experience' in sum) and ('required_experience' in num):
        print(sum['required_experience'], num['required_experience'])
        if num['required_experience'] > 0:
            avr_exp = sum['required_experience'] / num['required_experience']
            stats['vacancy_average_experience'] = avr_exp
    '''
    if ('employment_mode' in df) :
        emp_mod = df['employment_mode'].value_counts(normalize = True)
        stats['emp_mod'] =emp_mod.to_string()
    '''
    print(stats)
    return stats


def get_vacancy_graphics(df: pd.DataFrame):
    df.dropna(subset=[])


def get_cv_graphics(df: pd.DataFrame):
    df = df.dropna(subset=['salary', 'experience_years', 'experience_months'])
    df[df['salary_in'] == 'USD']['salary'] = df[df['salary_in'] == 'USD']['salary'] * 75
    df['experience_months'] = pd.to_numeric(df['experience_months'])
    df['experience_years'] = pd.to_numeric(df['experience_years'])
    df['general_experience'] = df['experience_months'] + df['experience_years'] * 12
    df = df.sort_values('general_experience')

    figure = df.plot(x='general_experience', y='salary', title='The dependency between experience and salary')
    figure.figure.savefig('templates/static/images/cv.png')


def get_cv_statistics(df: pd.DataFrame):
    sum = df.sum(axis = 0, skipna = True, numeric_only = True)
    num = df.count(axis = 0, numeric_only = True)
    stats = {}
    if ('salary' in sum) and ('salary' in num):
        if num['salary'] > 0:
            avr_slr = sum['salary'] / num['salary']
            stats['cv_average_salary'] = avr_slr
    if ('experience_years' in sum) and ('experience_years' in num):
        if num['experience_years'] > 0:
            avr_exp = sum['experience_years'] / num['experience_years']
            stats['cv_average_experience'] = avr_exp
    if ('age' in sum) and ('age' in num):
        if num['age'] > 0:
            avr_age = sum['age'] / num['age']
            stats['cv_average_age'] = avr_age
    '''
    if ('education' in df) :
        edu_sta = df['education'].value_counts(normalize = True)
        stats['edu_sta'] = edu_sta.to_string()
    '''
    print(stats)
    return stats
