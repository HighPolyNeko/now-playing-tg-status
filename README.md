# 🎧 SpotiBio

Показывает в «О себе» (bio) в Telegram, что ты слушаешь в Spotify прямо сейчас.

- Играет трек: `🎧 слушает: Исполнитель — Трек`
- Ничего не играет или пауза: `🎧 в наушниках тишина`

Работает бесплатно на GitHub Actions. Свой сервер и включённый компьютер не нужны.

## Как это работает

1. GitHub Actions по расписанию (раз в 5 минут) запускает `telegram_status.py`.
2. Скрипт через Spotify Web API узнаёт, какой трек играет сейчас.
3. Через Telegram API (библиотека [Telethon](https://github.com/LonamiWebs/Telethon)) он обновляет «О себе» в твоём аккаунте.
4. Если текст не изменился, запрос в Telegram не отправляется.

## Что в репозитории

| Файл | Зачем |
|---|---|
| `.github/workflows/spotify-status.yml` | Расписание и запуск в GitHub Actions |
| `telegram_status.py` | Основной скрипт: Spotify → bio в Telegram |
| `make_session.py` | Запускается один раз локально, выдаёт строку сессии Telegram |
| `get-refresh-token.main.kts` | Запускается один раз локально (Kotlin), выдаёт refresh token Spotify |

## Настройка

### 1. Приложение Spotify
1. Открой [Spotify Dashboard](https://developer.spotify.com/dashboard) и создай приложение.
2. Добавь Redirect URI: `http://127.0.0.1:8888/callback`
3. Скопируй **Client ID** и **Client secret**.

### 2. Refresh token Spotify
Нужен установленный Kotlin и JDK. Запусти локально:

```
kotlin get-refresh-token.main.kts <CLIENT_ID> <CLIENT_SECRET>
```

В браузере подтверди доступ. Скрипт напечатает refresh token.

### 3. Данные Telegram
1. На [my.telegram.org](https://my.telegram.org) в разделе «API development tools» создай приложение и скопируй `api_id` и `api_hash`.
2. Локально (нужен Python):

```
pip install telethon
python make_session.py
```

Введи `api_id`, `api_hash`, номер телефона и код из Telegram. Скрипт напечатает строку сессии.

### 4. Секреты репозитория
В репозитории: Settings → Secrets and variables → Actions → New repository secret. Добавь:

| Имя | Значение |
|---|---|
| `SPOTIFY_CLIENT_ID` | Client ID приложения Spotify |
| `SPOTIFY_CLIENT_SECRET` | Client secret приложения Spotify |
| `SPOTIFY_REFRESH_TOKEN` | Токен из шага 2 |
| `TG_API_ID` | `api_id` из шага 3 |
| `TG_API_HASH` | `api_hash` из шага 3 |
| `TG_SESSION` | Строка сессии из шага 3 |

### 5. Запуск
Вкладка **Actions** → **spotify-status** → **Run workflow**. Дальше запуски идут сами по расписанию.

## Настройки

- Текст для «ничего не играет»: константа `IDLE` в начале `telegram_status.py`.
- Префикс перед названием трека: константа `PREFIX` там же.
- Лимит длины bio: переменная окружения `TG_BIO_LIMIT` (по умолчанию 70 символов, у Premium лимит больше). Слишком длинное название обрезается с многоточием.

## Ограничения

- Расписание GitHub Actions не чаще чем раз в 5 минут, запуски бывают с задержкой. Это не реальное время, короткие треки могут не попасть в bio.
- В публичных репозиториях GitHub отключает запуски по расписанию после 60 дней без активности. Тогда workflow нужно включить вручную во вкладке Actions.
- Вход в Telegram идёт с серверов GitHub. Telegram может показать уведомление о новом входе.

## Безопасность

- **Строка сессии Telegram даёт полный доступ к аккаунту.** Храни её только в секретах репозитория, никому не показывай и не коммить в код. Если она утекла, завершите сессию в Telegram: «Настройки» → «Устройства».
- Так же храни в секрете `SPOTIFY_CLIENT_SECRET` и `SPOTIFY_REFRESH_TOKEN`.
- Автоматизация обычного аккаунта Telegram формально может нарушать правила сервиса. Используй на свой риск.
