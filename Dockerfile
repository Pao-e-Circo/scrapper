FROM python:3.15.0a1-trixie

RUN apt-get update

WORKDIR /code

COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY . /code

ENV paoecirco.org_attendences_folder=/data/attendences

CMD ["bash"]