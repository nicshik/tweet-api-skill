# TwitterAPI X Reader

[![CI](https://github.com/nicshik/tweet-api-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/nicshik/tweet-api-skill/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Портативный навык и вспомогательные скрипты для работы с X (Twitter) через `twitterapi.io`.

[🇬🇧 Read in English](README.md)

## Обзор

Этот репозиторий упаковывает переиспользуемый навык и терминальные команды для чтения твитов, X Articles, скачивания видео из твитов и вызова других документированных методов `twitterapi.io` без зависимости от прямого отображения `x.com`.

Он подходит, если вам нужны:

- портативная установка навыка в `~/.codex/skills/twitterapi-x-reader`;
- простые команды `xread`, `xapi` и `xmedia`;
- стабильный способ получать данные из X для исследований, кратких пересказов и структурированного извлечения.

Проект не связан с X Corp., Twitter или `twitterapi.io`.

Сопровождающий: [`nicshik`](https://github.com/nicshik).

## Что входит

- `SKILL.md` для агентных сред, которые поддерживают навыки.
- `agents/openai.yaml` с метаданными для интерфейса.
- `references/` с быстрым стартом, человекочитаемыми заметками и исследовательскими примерами.
- `scripts/` с Python-скриптами.
- `bin/xread`, `bin/xapi` и `bin/xmedia` как терминальные обёртки.
- `install_portable.sh` для установки и обновления.

## Требования

- Python 3.10 или новее.
- `zsh`, `rsync` и `install` для `install_portable.sh`.
- API-ключ `twitterapi.io`.

## Установка

### Установка портативного навыка

Из корня репозитория:

```bash
chmod +x ./install_portable.sh
./install_portable.sh
```

Затем создайте локальный файл с ключом, если его ещё нет:

```bash
mkdir -p ~/.codex/skills/twitterapi-x-reader
printf '%s\n' 'TWITTERAPI_IO_KEY=your_key_here' > ~/.codex/skills/twitterapi-x-reader/.env.local
```

Если в вашем shell путь `~/.local/bin` ещё не добавлен в `PATH`, добавьте его.

### Пакетная установка командной строки

Если нужны только команды `xread`, `xapi` и `xmedia`, установите пакет напрямую:

```bash
python -m pip install "git+https://github.com/nicshik/tweet-api-skill.git"
```

Пакетная установка не устанавливает файлы навыка Codex. Для авторизации используйте `TWITTERAPI_IO_KEY` или `--api-key`.

## Быстрый старт

Получить твит или статью:

```bash
xread "https://x.com/ZenithTON/status/2046570503801119055"
```

Принудительно читать как статью:

```bash
xread "2046570503801119055" --mode article
```

Скачать лучший MP4-вариант видео из твита:

```bash
xmedia "https://x.com/Yoda4ever/status/2049680135658336270?s=20" --output-dir ./downloads
```

`xmedia` печатает JSON с путём к сохранённому файлу, размером в байтах, исходной ссылкой на медиа, bitrate и media key. Скачивание ограничено HTTPS-ссылками под `video.twimg.com`.

Вызвать любой документированный метод API:

```bash
xapi --method GET --path /oapi/my/info --query-json '{}'
```

По умолчанию `xapi` принимает официальные пути API. Полные URL разрешены только для `https://api.twitterapi.io`, чтобы API-ключ не отправлялся на произвольные хосты.

Изменяющие HTTP-методы заблокированы без флага `--allow-mutation`:

```bash
xapi --method POST --path /twitter/post/create --body-json '{"text":"draft"}' --allow-mutation
```

## Выгрузка видео

Если навык установлен, выгрузка видео запускается глобальной командой:

```bash
xmedia "<tweet-url-or-id>" --output-dir ./downloads
```

Прямой вызов скрипта внутри установленного навыка:

```bash
python3 ~/.codex/skills/twitterapi-x-reader/scripts/twitterapi_media.py "<tweet-url-or-id>" --output-dir ./downloads
```

Команда записывает один или несколько `.mp4` файлов и печатает JSON такого вида:

```json
{
  "kind": "media_download",
  "tweet_id": "2049680135658336270",
  "files": [
    {
      "path": "/absolute/path/to/2049680135658336270-media-1-2176000.mp4",
      "bytes": 5744965,
      "bitrate": 2176000,
      "media_key": "13_2049617901142118400",
      "url": "https://video.twimg.com/..."
    }
  ],
  "source": "twitterapi.io"
}
```

Полезные флаги:

- `--output-dir ./downloads` задаёт директорию для сохранения.
- `--first` скачивает только первое видео из твита.
- `--filename name.mp4` задаёт имя файла, если выбран ровно один файл.
- `--overwrite` заменяет существующий файл.

## Практические сценарии

Прочитать твит или X Article и затем разобрать содержимое:

```bash
xread "https://x.com/ZenithTON/status/2046570503801119055"
```

Получить профиль автора:

```bash
xapi --method GET --path /twitter/user/info --query-json '{"userName":"ZenithTON"}'
```

Получить последние твиты автора:

```bash
xapi --method GET --path /twitter/user/last_tweets --query-json '{"userName":"ZenithTON","includeReplies":false}'
```

Посмотреть ответы:

```bash
xapi --method GET --path /twitter/tweet/replies/v2 --query-json '{"tweetId":"2046570503801119055","queryType":"Latest"}'
```

Посмотреть цитирования:

```bash
xapi --method GET --path /twitter/tweet/quotes --query-json '{"tweetId":"2046570503801119055","includeReplies":false}'
```

Найти аккаунты по теме:

```bash
xapi --method GET --path /twitter/user/search --query-json '{"query":"TON AI"}'
```

Найти твиты по теме:

```bash
xapi --method GET --path /twitter/tweet/advanced_search --query-json '{"query":"\"AI agents\" Telegram TON","queryType":"Top"}'
```

Скачать видео из твита для дальнейшей обработки:

```bash
xmedia "https://x.com/Yoda4ever/status/2049680135658336270?s=20" --output-dir ./downloads --overwrite
```

Если в твите несколько видео, `xmedia` по умолчанию скачивает все. Используйте `--first`, чтобы скачать только первое, или `--filename custom-name.mp4`, когда выбран ровно один файл.

Больше примеров:

- `references/research_examples.md`
- `references/capabilities.md`
- `references/api_quickstart.md`
- `references/endpoint_catalog.md`

## Работа с API-ключом

Репозиторий не хранит API-ключи.

Ожидаемый локальный файл с ключом:

```text
~/.codex/skills/twitterapi-x-reader/.env.local
```

Пример:

```text
TWITTERAPI_IO_KEY=your_key_here
```

Скрипты также принимают `--api-key`, но переменные окружения или `.env.local` предпочтительнее: аргументы командной строки могут попадать в историю shell.

## Разработка

Запустить тесты без сетевых вызовов:

```bash
python -m unittest discover -s tests
```

Проверить локальные ссылки в документации:

```bash
python scripts/check_links.py
```

Проверить точки входа пакета локально:

```bash
python -m pip install .
xapi --help
xread --help
xmedia --help
```

Проверить метаданные навыка валидатором Skill Creator, если он доступен:

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
```

## Поддержка и безопасность

Для вопросов, ошибок и запросов на улучшения используйте GitHub Issues.

Об уязвимостях сообщайте приватно через `SECURITY.md`. Не открывайте публичные задачи с API-ключами, `.env.local`, приватными данными аккаунтов или деталями эксплуатации.

## Обновление

После получения новых изменений из репозитория обновите портативную установку:

```bash
./install_portable.sh
```

Команда обновляет установленный навык и глобальные обёртки, сохраняя локальный файл `.env.local`.

Старые локальные установки в `~/.codex/skills/twitterapi_x_reader` определяются во время установки. Установщик при необходимости копирует старый `.env.local` в новую директорию навыка с hyphen-case именем, а `xread`, `xapi` и `xmedia` всё ещё проверяют старый путь для совместимости.

## Заметки

- По умолчанию инструмент работает в режиме только для чтения.
- Изменяющие методы API нужно использовать только намеренно.
- Скачивание медиа записывает локальные файлы и ограничено доменом `video.twimg.com`.
- `certifi` поддерживается, если он доступен, но скрипты могут использовать и системное хранилище сертификатов.
- Перед публикацией логов, примеров или отчётов об ошибках смотрите `SECURITY.md`.

## Лицензия

MIT
