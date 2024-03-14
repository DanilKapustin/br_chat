# Bank of Russia Chatbot Server

## Описание

Bank of Russia Chatbot - серверная часть.

## Зависимости

1. PostgreSQL
2. Redis
3. Python 3.10+
4. Poetry
5. E5 модель для эмбеддингов:

        git clone https://huggingface.co/intfloat/multilingual-e5-base

## Установка

1. Инициализировать БД:

        CREATE DATABASE br;
        CREATE USER br WITH PASSWORD 'br';        
        GRANT ALL PRIVILEGES ON DATABASE br TO br;
        GRANT ALL PRIVILEGES ON SCHEMA public TO br;
        \c br
        CREATE EXTENSION IF NOT EXISTS hstore;
 
2. Установить библиотеки:

        poetry install

        poetry shell
        python -m spacy download en_core_web_sm
        python -m spacy download ru_core_news_sm

3. Установить библиотеку llama.cpp:
   1. Для инференса на CPU:
             
          pip install llama-cpp-python
   
   2. Для инференса на GPU:
   
          CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python

## Запуск

1. Запуск Chroma DB сервера:

        chroma run --port 7777 --path /opt/llmui/db

2. Запуск API:

        uvicorn main:app --reload

3. Запуск background воркера:

        export E5_MODEL_PATH="path/to/multilingual-e5-base"
        saq -m task.settings --web

## Сборка

Для сборки подготовлено два Dockerfile: `cpu.Dockerfile` и `gpu.Dockerfile`. 
Первый подходит для запуска на CPU, второй - на GPU (NVIDIA).

Dockerfile содержит 2 целевых стадии: `api` and `background`. Для того, чтобы выполнить обе, запустите следующие 
команды:

    docker build --target api -t br-api . -f cpu.Dockerfile
    docker build --target background -t br-background . -f cpu.Dockerfile

## Миграции

Создать миграцию:

    alembic revision --autogenerate -m "message"

Апгрейд:

    alembic upgrade head

