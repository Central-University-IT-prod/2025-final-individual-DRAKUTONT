# Рекламная платформа PROD Backend 2025

Платформа для таргетированной рекламы, оптимизирующая прибыль, релевантность и выполнение лимитов кампаний. Построена на **Django Ninja** с использованием **PostgreSQL**, **Redis**, **Minio** и интеграцией с **Yandex GPT**.

---

## Инструкция по запуску

### Запуск
```bash
cd solution
docker-compose up --build
```

#### Сервисы в docker-compose.yml
- **app**: Django (порт 8080), Gunicorn через entrypoint.sh
- **postgres**: PostgreSQL 16.6 (порт 5432)
- **redis**: Redis 7.4 (порт 6379) — кэш текущего дня и тогл модерации
- **minio**: Minio (порт 9000) — хранение изображений
- **prometheus**: Prometheus (порт 9090) — мониторинг
- **grafana**: Grafana (порт 3000) — визуализация статистики

#### Переменные окружения(заданы в docker-compose)
- DJANGO_DEBUG=
- POSTGRES_CONN=
- REDIS_HOST=
- MINIO_STORAGE_ENDPOINT=
- YANDEX_GPT_API_KEY=

## Демонстрация работы
**Вы можете посмотреть openapi спецификацию по адресу http://localhost:8080/docs или скачать файл [openapi.yaml](docs/openapi.yaml), [openapi.json](docs/openapi.json)**

![swagger](docs/swagger.png)

Запрос на создание клиента:
```json
[
  {
    "client_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "login": "Alexandr Shahov",
    "age": 28,
    "location": "Moscow",
    "gender": "MALE"
  }
]
```

Запрос на создание рекламной кампании:
```json
{
  "impressions_limit": 8,
  "clicks_limit": 8,
  "cost_per_impression": 1.50,
  "cost_per_click": 2.50,
  "ad_title": "Amazing Offer",
  "ad_text": "Get great savings now!",
  "start_date": 5,
  "end_date": 15,
  "targeting": {
    "gender": "MALE",
    "age_from": 25,
    "age_to": 40,
    "location": "Chicago"
  }
}
```

Остальные запросы, а также их подробное описание вы найдете в спецефикации.<br>
Во время запросов также можно получить следующие ошибки:

`400` - ошибка валидации данных. Формат ответа:
```json
{
  "message": "Ошибка в данных запроса."
}
```

`403` - клиент не может кликнуть на непросмотренное объявление. Формат ответа:
```json
{
  "message": "Запрещено"
}
```

`404` - клиент, кампания или рекламодатель не найден. Формат ответа:
```json
{
  "message": "Объект не найден"
}
```

### Дополнительный функционал

- Добавление изображений в рекламных объявлениях<br>
`/{advertiser_id}/campaigns/{campaign_id}/upload (POST)` - эндпоинт для добавления изображения.<br> Изображения хранятся в self-hosted хранилище [MinIO](https://github.com/minio)<br>
Админ панель находится по адресу http://localhost/9001/login. Логин и пароль - minioadmin

---

- Визуализация статистики<br><br>
Для визуализации статистики используется `grafana` и `prometheus`<br>
![grafana](docs/grafana.png)

Для того чтобы посмотреть статистику необходимо:
1. Зайти на http://localhost:3000/
2. Данные для авторизации - admin:admin
3. Data sources -> add data source -> prometheus
4. В поле connection вставить http://prometheus:9090
5. Save & test
6. Dashboards -> New -> Import
7. Импортировать файл [grafana_config](./grafana_config.json) -> load
8. Select Data Source -> Prometheus -> Import
---

- Модерация текстов рекламных кампаний<br><br>
Для модерации текстов используется YandexGPT Pro. Если LLM выявит нарушения, то клиент получит 400.<br><br>
Модерацию можно включать и отключать следующими эндпоинтами:
  - `/moderation/enable (POST)` - включение
  - `/moderation/disable (POST)` - выключение
  - `/moderation (GET)` - получение текущего состояния(хранится в `Redis`)<br>

---

- Интеграция с LLM для генерации рекламных текстов<br><br>
Для генерации рекламных текстов я использую YandexGPT Pro. Для того, чтобы сгенерировать текст надо отправить запрос на `/advertisers/{advertiser_id}/campaigns/generation (POST)`.<br><br>
**Запрос**:
    ```json
    {
        "product_name": "Смартфон X",
        "target_action": "Купить",
        "target_audience": "Молодежь 18-25 лет"
    }
  ```
    **Ответ**:
    ```json
    {
        "text": "Купи смартфон X со скидкой 20%! Идеально для молодежи, стильный и мощный!"
    }
    ```

## База данных
![erd](docs/erd.png)
  
Схему также можно посмотреть по [ссылке](https://www.drawdb.app/editor?shareId=005972ba041caf162cdb8b72fd356617)

### Модели и связи

| **Модель** 	|     **Описание**     	|                        **Связи**                        	|
|:----------:	|:--------------------:	|:-------------------------------------------------------:	|
|   `Client`   	|     Пользователь     	|      Campaign (ManyToMany через Impression, Click)      	|
| `Advertiser` 	|     Рекламодатель    	|              Campaign, MLScore (ForeignKey)
|  `Campaign`  	|  Рекламная кампания  	| Client (ManyToMany), Advertiser, Targeting (ForeignKey) 	|
|  `Targeting` 	| Параметры таргетинга 	|                  Campaign (ForeignKey)                  	|
| `Impression` 	|        Показы        	|              Client, Campaign (ForeignKey)              	|
|    `Click`   	|         Клики        	|              Client, Campaign (ForeignKey)              	|
|   `Mlscore`  	|     Релевантность    	|              Client, Campaign (ForeignKey)               	|

## Описание основных точек входа
**Вы можете посмотреть openapi спецификацию по адресу http://localhost:8080/docs или скачать файл [doc.json](docs/doc.json)**

#### `/ads?client_id={client_id} (GET)`
**Описание**: Возвращает подходящее рекламное объявление для клиента.

**Параметры**:
- `client_id` (UUID, обязательный): Идентификатор клиента.

**Логика**:
1. Получает клиента по `client_id`.
2. Фильтрует активные кампании по дате, таргетингу и лимитам (≤ 105%).
3. Вызывает `select_best_campaign` для выбора кампании с максимальным `score`:
   - Рассчитывает `profit`, `relevance`, `limit_factor`.
   - Нормализует метрики (`max` для < 10 кампаний, `linear` для ≥ 10).
   - Добавляет приоритетность тем кампаниям, которые скоро закончатся и не набрали необходимый процент показов.
   - Вычисляет `score = 0.5 * profit_norm + 0.25 * relevance_norm + 0.15 * limit_factor`.
4. Сохраняет показ в `Impression` и возвращает рекламу или 404.<br><br>
    ![alg](docs/alg.jpg)

## Обоснованность решения
 - `Django Ninja`: Использован как фреймворк для быстрого создания REST API с поддержкой OpenAPI. Выбран за простоту, производительность и интеграцию с Django
   
 - `PostgreSQL`: Гибкая, надежная и отказоустойчивая СУБД. Можно легко масштабировать
   
 - `Redis`: Использован для кэширования текущего дня (`time_emulation.cache`) и состояния модерации, обеспечивая низкую задержку и высокую скорость доступа. Выбран за простоту и популярность в задачах кэширования
   
 - `Minio`: Очень быстрое и легковесное хранилище для изображений, совместимое с S3. Легко интегрируется в django благодаря [django-minio-storage](https://django-minio-storage.readthedocs.io/en/latest/)
   
 - `Prometheus + Grafana`: Добавлены для мониторинга и визуализации статистики . Prometheus собирает метрики, а Grafana предоставляет интуитивные дашборды
   
 - `Yandex GPT`: Интегрирован для генерации текстов кампаний и модерации. Выбран за доступность и неплохие показатели модели. Рассматривался OpenAI, но Yandex GPT предпочтительнее из-за локализации и стоимости


## Тесты
Перед запуском тестов необходимо создать `.env` файл, со следующим содержимым:
```
DJANGO_DEBUG=True
POSTGRES_CONN=postgres://postgres:postgres@localhost:5432/advertising_platform
REDIS_HOST=localhost
REDIS_PORT=6379
YANDEX_GPT_MODEL_TYPE=yandexgpt
YANDEX_GPT_CATALOG_ID=b1gp8s6k8vk82fpui3b5
YANDEX_GPT_API_KEY=REDACTED
MINIO_STORAGE_ENDPOINT=localhost:9000
```
А также локально установить зависимости:
```bash
uv sync
```
*Если uv не установлен https://docs.astral.sh/uv/getting-started/installation/
```
Для запуска тестов необходимо запустить контейнер с postgres и redis(обязательно отключить модерацию), и выполнить команду:
```bash
python manage.py test .
```

![tests](docs/tests.png)