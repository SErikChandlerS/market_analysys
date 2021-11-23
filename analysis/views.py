from django.shortcuts import render, HttpResponseRedirect, redirect
from django.views import View
from .models import vacancy, cv, statistics
from src.parsing.vacancy import get_vacancies
from src.parsing.candidate import get_cvs
from src.analysis.market_analysis import get_vacancy_statistics, get_cv_statistics, get_cv_graphics, get_vacancy_graphics
from src.parsing.gs import upload_to_gs
import pandas as pd


# Create your views here.
class main_page(View):

    def post(self, request, *args, **kwargs):
        context = {}

        return HttpResponseRedirect(request.POST['redirect'])

    def get(self, request, *args, **kwargs):
        context = dict()
        return render(request, 'main_page.html', context)


class load_vacancies(View):

    def post(self, request, *args, **kwargs):
        vacancy.objects.filter(region=int(request.POST['region']), query=request.POST['vacancy_name']).delete()
        context = vacancy.objects.add_vacancies(
            get_vacancies(request.POST['vacancy_name'], int(request.POST['region'])))
        upload_to_gs("vacancy", request.POST['vacancy_name'], int(request.POST['region']))
        return HttpResponseRedirect('main_page')

    def get(self, request, *args, **kwargs):
        context = dict()
        return render(request, 'load_vacancies.html', context)


class load_cvs(View):

    def post(self, request, *args, **kwargs):
        cv.objects.filter(region=int(request.POST['region']), query=request.POST['vacancy_name']).delete()
        context = cv.objects.add_cvs(get_cvs(request.POST['vacancy_name'], int(request.POST['region'])))
        upload_to_gs("cv", request.POST['vacancy_name'], int(request.POST['region']))
        return HttpResponseRedirect('main_page')

    def get(self, request, *args, **kwargs):
        context = dict()
        return render(request, 'load_cvs.html', context)


class load_statistics(View):

    def post(self, request, *args, **kwargs):
        region = int(request.POST['region'])
        query = request.POST['query']

        queries = vacancy.objects.order_by().values_list('query', flat=True).distinct()
        context = {'queries': list(queries)}
        context.update(query=query, region=region)

        if 'show' in request.POST:
            if request.POST['show'] == 'cvs':
                context.update({
                    'headers': [field.name for field in cv._meta.get_fields()],
                    'table': list(cv.objects.filter(region=region, query=query).values())
                })
            if request.POST['show'] == 'vacancies':
                context.update({
                    'headers': [field.name for field in vacancy._meta.get_fields()],
                    'table': list(vacancy.objects.filter(region=region, query=query).values())
                })
            return render(request, 'table.html', context)

        choice = request.POST['choice']
        stats = list(statistics.objects.filter(region=region, query=query).values())

        context['statistics'] = stats
        if len(context['statistics']) == 0 or choice == 'update':
            statistics.objects.filter(region=region, query=query).delete()
            vacancies = list(vacancy.objects.filter(region=region, query=query).values())
            cvs = list(cv.objects.filter(region=region, query=query).values())
            stats = {}
            context['statistics'] = stats

            if 'vacancies' in request.POST and (len(vacancies) == 0 or choice == 'update'):
                vacancy.objects.filter(region=region, query=query).delete()
                vacancies = vacancy.objects.add_vacancies(get_vacancies(query, region))
                vacancies = vacancy.objects.filter(region=region, query=query).values()
                upload_to_gs("vacancy", query, region)
            df_vacancy = pd.DataFrame(vacancies)
            stats = get_vacancy_statistics(df_vacancy)

            if 'cvs' in request.POST and (len(cvs) == 0 or choice == 'update'):
                cv.objects.filter(region=region, query=query).delete()
                cvs = cv.objects.add_cvs(get_cvs(query, region))
                cvs = cv.objects.filter(region=region, query=query).values()
                upload_to_gs("cv", query, region)
            df_cv = pd.DataFrame(cvs)
            stats.update(get_cv_statistics(df_cv))

            stats.update(region=region, query=query)

            stats = statistics.objects.add_statistic(stats)
            print(stats)
            stats = list(statistics.objects.filter(region=region, query=query).values())
            context['statistics'] = stats

        cvs = cv.objects.filter(region=region, query=query).values()
        if len(cvs) > 0:
            get_cv_graphics(pd.DataFrame(cvs))
            context.update(cv_grapics=True)

        # vacancies = vacancy.objects.filter(region=region, query=query).values()
        # if len(vacancies) > 0:
        #     get_vacancy_graphics(pd.DataFrame(vacancies))
        #     context.update(vacancy_grapics=True)
        return render(request, 'load_statistics.html', context)

    def get(self, request, *args, **kwargs):
        queries = vacancy.objects.order_by().values_list('query', flat=True).distinct()
        context = {'queries': list(queries)}
        return render(request, 'load_statistics.html', context)
