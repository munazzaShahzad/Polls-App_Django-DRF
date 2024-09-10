FROM python:3.9.6-slim-buster

# Install dependencies for mysqlclient, including pkg-config
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

WORKDIR /app

COPY requirements.txt requirements.txt

# Install Python dependencies, including mysqlclient
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "django_site.asgi:application"]
