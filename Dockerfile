FROM python:3.8.20-slim

RUN apt-get update && apt-get install -y git
RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install --default-timeout=10000 -r requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgtk2.0-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*
RUN pip install python-dotenv langchain_groq langchain requests

EXPOSE 5000

COPY . /app
WORKDIR /app

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]