from django.db import models
from django.utils.translation import gettext_lazy as _


class vacancy_manager(models.Manager):
    def add_vacancy(self, vacancy: dict):
        entity = self.model(**vacancy).save()
        return entity

    def add_vacancies(self, vacancies: list):
        entity = [self.model(**vacancy).save() for vacancy in vacancies]
        return entity


class vacancy(models.Model):
    name = models.TextField(null=True)
    company_name = models.TextField(null=True)
    salary_from = models.IntegerField(null=True)
    salary_to = models.IntegerField(null=True)
    required_experience = models.TextField(null=True)
    employment_mode = models.TextField(null=True)
    schedule = models.TextField(null=True)
    key_skills = models.TextField(null=True)
    city = models.TextField(null=True)
    responsibility = models.TextField(null=True)
    requirement = models.TextField(null=True)
    link = models.TextField(null=True)
    link_to_company = models.TextField(null=True)
    hh_id = models.IntegerField()
    date = models.DateTimeField(null=True)
    salary_in = models.TextField(null=True)
    region = models.IntegerField()
    query = models.TextField()

    objects = vacancy_manager()

    class Meta:
        verbose_name = _('vacancy')
        verbose_name_plural = _('vacancies')

    def __str__(self):
        return "%s %s" % (self.name, self.company_name)

    def __int__(self):
        return self.name


class cv_manager(models.Manager):
    def add_cv(self, cv: dict):
        entity = self.model(**cv).save()
        return entity

    def add_cvs(self, cvs: list):
        entity = [self.model(**cv).save() for cv in cvs]
        return entity


class cv(models.Model):
    hh_id = models.IntegerField()
    name = models.TextField(null=True)
    link = models.TextField(null=True)
    age = models.IntegerField(null=True)
    salary = models.IntegerField(null=True)
    salary_in = models.TextField(null=True)
    experience_years = models.TextField(null=True)
    experience_months = models.TextField(null=True)
    last_work = models.TextField(null=True)
    sex = models.TextField(null=True)
    city = models.TextField(null=True)
    specialization_category = models.TextField(null=True)
    specializations = models.TextField(null=True)
    employment_modes = models.TextField(null=True)
    schedule = models.TextField(null=True)
    previous_positions = models.TextField(null=True)
    key_skills = models.TextField(null=True)
    education = models.TextField(null=True)
    languages = models.TextField(null=True)
    region = models.IntegerField()
    query = models.TextField()

    objects = cv_manager()

    class Meta:
        verbose_name = _('CV')
        verbose_name_plural = _('CVs')

    def __str__(self):
        return self.name

    def __int__(self):
        return self.name


class statistics_manager(models.Manager):
    def add_statistic(self, statistic: dict):
        entity = self.model(**statistic).save()
        return entity


class statistics(models.Model):
    vacancy_average_from = models.IntegerField(verbose_name="Average starting salary", null=True)
    vacancy_average_to = models.IntegerField(verbose_name="Average ending salary", null=True)
    vacancy_average_experience = models.IntegerField(verbose_name="Average experience", null=True)

    cv_average_salary = models.IntegerField(verbose_name="Average salary", null=True)
    cv_average_experience = models.IntegerField(verbose_name="Average experience", null=True)
    cv_average_age = models.IntegerField(verbose_name="Average age", null=True)

    region = models.IntegerField()
    query = models.TextField()

    objects = statistics_manager()

    class Meta:
        verbose_name = _('Statistic')
        verbose_name_plural = _('Statistics')

    def __str__(self):
        return "%s %s" % (self.query, self.region)

    def __int__(self):
        return "%s %s" % (self.query, self.region)
