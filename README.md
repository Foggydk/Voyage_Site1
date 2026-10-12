# Вояж-Тур — статический сайт

Многостраничный сайт на HTML и Tailwind CSS (CDN). Дизайн-система: [vibrant_horizon/DESIGN.md](vibrant_horizon/DESIGN.md).

## Страницы

| URL | Раздел |
|-----|--------|
| `/` | Перенаправление на туры |
| `/tours/` | Поиск туров |
| `/treatment/` | Медицинский туризм |
| `/destinations/` | Направления |
| `/about/` | О компании |
| `/account/` | Личный кабинет |
| `/login/` | Вход |

## Запуск локально

**Рекомендуется** — локальный сервер (корректные относительные пути и навигация):

```bash
cd stitch_
npm start
```

или без npm:

```bash
npx --yes serve .
```

Откройте в браузере адрес из терминала (обычно `http://localhost:3000`) и перейдите на `/tours/`.

**Быстрый способ** — открыть `index.html` в браузере (двойной клик). Для перехода между разделами используйте меню в шапке.

## Стили кнопок

Общие классы в [assets/css/site.css](assets/css/site.css):

- `btn btn-primary` — красная кнопка, при наведении переходит в оранжевый
- `btn btn-secondary` — белая с красной обводкой
- `btn btn-ghost` — полупрозрачная «стеклянная»

Учитывается `prefers-reduced-motion: reduce`.

## База данных (PostgreSQL)

После настройки DBeaver:

1. В DBeaver выполните скрипт [server/schema.sql](server/schema.sql) (создаёт таблицу `users`).
2. Скопируйте `server/.env.example` → `server/.env` и укажите `DATABASE_URL` (как в DBeaver: пользователь, пароль, хост, порт, имя базы).
3. Создайте тестового пользователя: `npm run db:seed` (из папки `stitch_`).
4. Запустите сайт с API: `npm run server` → откройте `http://localhost:3001/login/`.
5. Вход: `test@voyage.ru` / `password123`.

Проверка связи с БД: `http://localhost:3001/api/health`.

> Старый `npm start` (только статика) не подключает PostgreSQL — для входа нужен `npm run server`.

## Требования

- Интернет (Tailwind CDN, Google Fonts, изображения)
- Для `npm start` / `npm run server`: Node.js
- Для входа в кабинет: PostgreSQL

## Пересборка страниц

Если правите исходники в `_1`…`_6/code.html`:

```bash
python scripts/build-pages.py
```
