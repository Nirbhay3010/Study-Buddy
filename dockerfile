FROM python:3.9-buster
RUN python -m pip install -U --force-reinstall pip
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
        libjpeg-dev zlib1g-dev
    

# Set work directory
RUN mkdir /code
WORKDIR /code

# Copy project code
COPY . /code/
RUN python3 -m pip install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

