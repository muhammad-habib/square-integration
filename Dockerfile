FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN pip3 install -r req-latest.txt
CMD ["python", "./wyspp/manage.py runserver 0.0.0.0:80"]