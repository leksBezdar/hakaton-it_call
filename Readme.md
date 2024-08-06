# Сервис для хакатона под названием "ИТ-вызов"

## Оглавление

- [Функциональные возможности](#функциональные-возможности)
- [Технологический стек](#технологический-стек)
- [Архитектура](#архитектура)
- [Начало работы](#начало-работы)
  - [Предварительные требования](#предварительные-требования)
  - [Установка](#установка)
  - [Запуск проекта](#запуск-проекта)
- [Документация API](#документация-api)
- [Вклад в проект](#вклад-в-проект)

## Функциональные возможности

- Авторизация с помощью одноразового пароля (OTP)
- Отправка напоминаний по электронной почте

## Технологический стек

- **Фреймворк:** FastAPI
- **База данных:** PostgreSQL, Redis
- **Брокер сообщений:** Aiokafka
- **Контейнеризация:** Docker, Docker Compose

## Архитектура

Этот проект организован с использованием упрощенного подхода Domain-Driven Design (DDD).

## Начало работы

### Предварительные требования

Убедитесь, что на вашем компьютере установлены следующие программы:

- Docker
- Docker Compose
- GNU Make (Опционально, сильно упрощает работу с сервисом)

### Установка

1. Клонируйте репозиторий:

    ```sh
    git clone https://github.com/leksbezdar/hakation-it_call.git
    cd hakation-it_call
    ```

2. Создайте файл `.env` в корневом каталоге проекта и добавьте в него переменные окружения. Вы можете использовать `.env.example` как образец.

    ```sh
    cp .env.example .env
    ```

### Запуск проекта

1. Соберите и запустите Docker-контейнеры через Makefile:

    ```sh
    make all
    ```
    
или напрямую через docker-compose:

  ```sh
  docker compose -f docker_compose/storages.yaml -f docker_compose/app.yaml -f docker_compose/redis.yaml -f docker_compose/kafka.yaml --env-file .env up --build -d
  ```

2. Приложение будет доступно по адресу `http://0.0.0.0:8000`.

3. Вы можете использовать эту команду для запуска только хранилищ:

    ```sh
    make storages
    ```

4. Вы можете выполнить миграцию базы данных:

    ```sh
    make upgrade
    ```

5. Вы можете создать новые миграции:

    ```sh
    make revision name="Название вашей миграции"
    ```

6. Вы можете использовать эту команду для остановки приложения:

    ```sh
    make app-down
    ```

Другие команды доступны для просмотра в Makefile.

## Документация API

Документация API автоматически генерируется с помощью OpenAPI и доступна по адресу `http://0.0.0.0:8000/docs`.

## Вклад в проект

Вклады приветствуются! Пожалуйста, следуйте этим шагам:

1. Форкните репозиторий.
2. Создайте новую ветку (`git checkout -b feature/YourFeature`).
3. Зафиксируйте свои изменения (`git commit -m 'Добавить новую функцию'`).
4. Отправьте ветку в удаленный репозиторий (`git push origin feature/YourFeature`).
5. Откройте pull request.

Не стесняйтесь исследовать и модифицировать проект по мере необходимости для своих нужд!

## Дополнения к кейсу
**Ссылка на кейс**: https://itcube18.ru/#/ITChallenge

### Сроки проекта
1. **Дистанционный этап**: образовательная программа для участников,
начало работы над кейсовым заданием – с 01 июля по 10 августа 2024 года;
2. **Очный этап Хакатона**: 23 – 24 августа 2024 год

### Описание проекта

Новогодний адвент по цифровой гигиене «Кибербезопасный Новый год» направлен на предоставление практических рекомендаций и советов в области кибергигиены. Последовательное выполнение этих рекомендаций поможет создать безопасную цифровую среду и встретить наступающий год кибербезопасно. Каждый день открывается новое окно с информацией, сохраняя доступность предыдущих окон.

### Функциональные требования

1. **Кнопка подписаться**: Вызывает модальное окно с формой отправки данных пользователя (email, никнейм, имя пользователя в Telegram) и согласием на обработку персональных данных.
2. **Кнопка авторизоваться**: Вызывает модальное окно с формой ввода email, затем форму для ввода одноразового пароля, который был направлен на почту.
3. **Баннер с соглашением на использование cookie**: Необходимо добавить баннер для аутентификации пользователя с использованием cookie.

### Серверная часть

1. **База данных**: Используется PostgreSQL (желательно) или MySQL (допустимо).
2. **Фреймворки**: Django или FastAPI.
3. **Email-рассылка**: Реализовать отправку писем о новых рекомендациях и авторизационные письма с одноразовым кодом. Шаблон писем должен включать логотип компании, ссылку на сайт, строгий стиль, шрифт одного типа, размер текста от 14 px до 24 px. В шаблоне рассылок должна быть гиперссылка "Отписаться от рассылки".

Проект приветствует любые дополнения, не описанные в задании.
