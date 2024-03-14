# Bank of Russia Chatbot

## Зависимости

1. https://huggingface.co/intfloat/multilingual-e5-base
2. Saiga 7B на основе Mistral для инференса https://huggingface.co/IlyaGusev/saiga_mistral_7b_gguf/blob/main/model-q8_0.gguf
3. Windows(WSL 2)/Linux/Mac OS для сборки 

## Зависимости
Файлы для датасета можно брать из Dataset.zip

## Конфигурация

1. Скопируйте файл `docker/.env.example` в `docker/.env`
2. Установите значения переменных окружения в файле `docker/.env`:
   - API_WORKERS - количество воркеров для API
   - API_PORT - порт для API
   - API_DOMAIN - домен для API
   - API_URL - URL для API (должен быть в формате http(s)://${API_DOMAIN}:${API_PORT})
   - API_CORS_ORIGIN - URL фронтенда (должен быть в формате http(s)://${UI_DOMAIN}:${UI_PORT})
   - BACKGROUND_WORKERS - количество воркеров для фоновых задач
   - UI_PORT - порт для фронтенда
   - UI_DOMAIN - домен для фронтенда

## Сборка

Выполните следующую команду для сборки Docker образов (gpu - для запуска на GPU, опционально):

    bin/build.sh [gpu]

## Запуск

### Копирование образов

1. Экспортируйте собранные образы в архив:

        docker save -o br-chatbot.tar br-api br-background br-ui

2. Скопируйте собранные образы на сервер, на котором будет запускаться приложение:

        scp br-chatbot.tar ${USER}@${HOST}:${PATH}

3. (на сервере) Загрузите образы на сервер:

        docker load -i br-chatbot.tar

4. Скопируйте следующие файлы и директории на сервер, на котором будет запускаться приложение:
   * .env
   * docker-compose.yml
   * docker-compose.https.yml (если вы хотите запустить приложение по протоколу HTTPS)
   * bin/
   * docker/

### Запуск по протоколу HTTP

1. Выполните следующую команду для запуска приложения (gpu - для запуска на GPU, опционально):

        bin/start-http.sh [gpu]

2. Скопируйте модель [E5](https://huggingface.co/intfloat/multilingual-e5-base) в вольюм `model_data`, подпапку `e5`
3. Скопируйте модель Saiga 7B в вольюм `model_data`, подпапку `saiga`
4. Откройте ваш браузер и пройдите по ссылке ${API_CORS_ORIGIN}

### Запуск по протоколу HTTPS

1. Выполните следующую команду для генерации сертификатов (замените `${API_DOMAIN}` и `${UI_DOMAIN}` на домены, которые 
вы хотите использовать для API и UI соответственно):

        bin/generate-certs.sh ${API_DOMAIN}
        bin/generate-certs.sh ${UI_DOMAIN}

2. Выполните следующую команду для запуска приложения (gpu - для запуска на GPU, опционально):

        bin/start-https.sh [gpu]

3. Остальные шаги аналогичны шагам для HTTP-only
4. Для обновления сертификатов выполните следующие команды:

        bin/renew-certs.sh

## Для регистрации и авторизации
API_CORS_ORIGIN+/login 
API_CORS_ORIGIN+/register
(API_CORS_ORIGIN - вы можете изменить в .env, который находится в дериктории docker)

## Для работы модели не забудьте 
Во вкладке Модели -> Выбираем модель -> Передать полый путь до модели

## Выключение

Для того, чтобы остановить и удалить все контейнеры, запустите:

    bin/down.sh
