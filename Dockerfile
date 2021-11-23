FROM python:3

RUN mkdir /app
WORKDIR /app


RUN apt-get clean && apt-get update && apt-get install -y locales
RUN sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
RUN locale-gen ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8
ENV LC_TIME ru_RU.UTF-8


COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

CMD ["python", "manage.py", "runserver"]
