# Развёртывание бота на Timeweb Cloud

Краткая инструкция, как залить и запустить бота на вашем VPS в Timeweb Cloud.

---

## Быстрый старт (root, Ubuntu 20.04, requirements уже загружены)

Если вы под **root** на **Ubuntu 20.04** и **requirements.txt уже на сервере** в `/opt/svadbabot/`:

```bash
# 1. Подключиться
ssh root@ВАШ_IP

# 2. Перейти в каталог и создать venv (если ещё не создан)
cd /opt/svadbabot
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 3. Создать .env с токеном и Admin ID
nano .env
```
В .env минимум (подставьте свои значения). Если Telegram блокируют — добавьте прокси:
```
TELEGRAM_BOT_TOKEN=7586435661:AAGYqwdOF8uXuGBy0yGEv4pqyJecCl2BS1k
TELEGRAM_ADMIN_ID=884422112
# Прокси для обхода блокировки (например, в РФ):
# PROXY_HTTP=http://proxy.example.com:8080
# PROXY_USER=user
# PROXY_PASSWORD=password
```
Сохранить: Ctrl+O, Enter, Ctrl+X.

```bash
# 4. Скопировать сервис (если папка deploy есть) или создать вручную
cp deploy/svadbabot.service /etc/systemd/system/
# или: nano /etc/systemd/system/svadbabot.service — вставить содержимое из deploy/svadbabot.service

# 5. Включить и запустить
systemctl daemon-reload
systemctl enable svadbabot
systemctl start svadbabot
systemctl status svadbabot
```

Логи в реальном времени: `journalctl -u svadbabot -f`. Перезапуск: `systemctl restart svadbabot`.

---

## Прокси для сервера в Москве (пошагово)

Сервер в Москве → Telegram с него блокируют. Нужен HTTP-прокси за границей. Что делать по шагам.

### Шаг 1. Получить прокси

Нужен **HTTP-прокси** (адрес вида `http://хост:порт` или `http://логин:пароль@хост:порт`). Варианты:

| Вариант | Что делать |
|--------|-------------|
| **Платный прокси** | Купить HTTP(S) прокси у любого провайдера (поиск: «HTTP прокси для API»). Вам дадут: хост, порт, иногда логин и пароль. |
| **Свой прокси за границей** | Арендовать дешёвый VPS за рубежом (например Нидерланды), поднять на нём Squid — получится свой HTTP-прокси. |
| **VPN с HTTP-прокси** | Некоторые VPN дают не только клиент, но и данные для HTTP-прокси (хост:порт, логин, пароль) — если есть, можно использовать их. |

Сохраните: **хост**, **порт**, и если есть — **логин** и **пароль**.

---

### Шаг 2. Подключиться к серверу по SSH

На своём компьютере (PowerShell или cmd):

```bash
ssh root@IP_ВАШЕГО_СЕРВЕРА
```

IP смотрите в панели Timeweb Cloud. Введите пароль (или используйте ключ), если попросит.

---

### Шаг 3. Открыть файл .env на сервере

На сервере выполните:

```bash
cd /opt/svadbabot
nano .env
```

Должны открыться уже сохранённые строки с токеном и Admin ID. Если файла нет — просто введите все строки с нуля (в том числе токен и ADMIN_ID).

---

### Шаг 4. Добавить (или изменить) строки прокси в .env

В том же файле `.env` добавьте или отредактируйте строки прокси.

**Если прокси без логина и пароля** (только хост и порт):

```env
PROXY_HTTP=http://ХОСТ:ПОРТ
```

Пример:
```env
PROXY_HTTP=http://proxy.example.com:8080
```

**Если прокси с логином и паролем** — три строки:

```env
PROXY_HTTP=http://ХОСТ:ПОРТ
PROXY_USER=ваш_логин
PROXY_PASSWORD=ваш_пароль
```

Пример:
```env
PROXY_HTTP=http://proxy.example.com:3128
PROXY_USER=myuser
PROXY_PASSWORD=mysecret123
```

Итоговый `.env` может выглядеть так:

```env
TELEGRAM_BOT_TOKEN=7586435661:AAGYqwdOF8uXuGBy0yGEv4pqyJecCl2BS1k
TELEGRAM_ADMIN_ID=884422112
PROXY_HTTP=http://ваш-прокси-хост:порт
PROXY_USER=логин
PROXY_PASSWORD=пароль
```

(Строки `PROXY_USER` и `PROXY_PASSWORD` — только если прокси с авторизацией.)

---

### Шаг 5. Сохранить файл и выйти из nano

- **Сохранить:** `Ctrl+O`, затем `Enter`.
- **Выйти:** `Ctrl+X`.

---

### Шаг 6. Перезапустить бота

На сервере выполните:

```bash
systemctl restart svadbabot
```

Проверить, что сервис запущен:

```bash
systemctl status svadbabot
```

Должно быть `active (running)` зелёным. Если `failed` — смотрите логи (шаг 7).

---

### Шаг 7. Проверить логи (если что-то не работает)

```bash
journalctl -u svadbabot -n 80 --no-pager
```

Или в реальном времени:

```bash
journalctl -u svadbabot -f
```

Выход: `Ctrl+C`. Если в логах ошибка подключения к Telegram или к прокси — проверьте хост/порт/логин/пароль в `.env` и что прокси вообще доступен с вашего сервера.

---

### Кратко: куда что писать

| Что | Куда |
|-----|------|
| Хост и порт прокси | В файле `/opt/svadbabot/.env` — строка `PROXY_HTTP=http://хост:порт` |
| Логин и пароль прокси (если есть) | В том же `.env` — строки `PROXY_USER=...` и `PROXY_PASSWORD=...` |
| После изменений | Выполнить на сервере: `systemctl restart svadbabot` |

---

## Что нужно (общая часть)

- Сервер с Linux (Ubuntu 20.04 / 22.04) в Timeweb Cloud  
- SSH-доступ к серверу  
- Токен и Admin ID задаются в `.env` на сервере  

---

## 1. Подключиться к серверу по SSH

Из панели Timeweb Cloud возьмите IP сервера и способ входа (пароль или SSH-ключ). Пример:

```bash
ssh root@ВАШ_IP
```

---

## 2. Установить Python 3 и venv (если ещё не установлены)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

---

## 3. Каталог и файлы

Каталог бота: `/opt/svadbabot/`. В нём должны быть `botyuli.py` и `requirements.txt`. Загрузка с ПК:

```bash
scp botyuli.py requirements.txt root@ВАШ_IP:/opt/svadbabot/
```

При необходимости можно залить и папку `deploy` (для systemd unit).

---

## 4. Виртуальное окружение и зависимости

На сервере (под root):

```bash
cd /opt/svadbabot
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
```

---

## 5. Переменные окружения (.env)

Создайте файл с токеном и Admin ID:

```bash
nano /opt/svadbabot/.env
```

Содержимое (подставьте свои значения). Для обхода блокировки Telegram добавьте `PROXY_HTTP`, при необходимости `PROXY_USER` и `PROXY_PASSWORD`:

```
TELEGRAM_BOT_TOKEN=7586435661:AAGYqwdOF8uXuGBy0yGEv4pqyJecCl2BS1k
TELEGRAM_ADMIN_ID=884422112
PROXY_HTTP=http://ваш-прокси:порт
```

Сохраните: Ctrl+O, Enter, Ctrl+X. По желанию: `chmod 600 /opt/svadbabot/.env`.

---

## 6. Запуск через systemd (root, Ubuntu)

Скопировать unit в systemd:

```bash
cp /opt/svadbabot/deploy/svadbabot.service /etc/systemd/system/
```

Если папки `deploy` нет — создать сервис вручную:

```bash
nano /etc/systemd/system/svadbabot.service
```

Вставить содержимое из `deploy/svadbabot.service` (там уже `User=root`, `Group=root`). Затем:

```bash
systemctl daemon-reload
systemctl enable svadbabot
systemctl start svadbabot
systemctl status svadbabot
```

Логи: `journalctl -u svadbabot -f`. Перезапуск: `systemctl restart svadbabot`.

---

## 7. Тестовый запуск (без systemd)

Чтобы просто проверить, что бот отвечает:

```bash
cd /opt/svadbabot
export TELEGRAM_BOT_TOKEN="ваш_токен"
export TELEGRAM_ADMIN_ID=884422112
./venv/bin/python botyuli.py
```

Остановка — Ctrl+C. Для постоянной работы используйте systemd (шаг 6).

---

## Итог

- Файлы бота лежат в `/opt/svadbabot/` (или в выбранной вами папке).  
- Токен и Admin ID задаются в `/opt/svadbabot/.env`.  
- Сервис `svadbabot` при падении перезапускается и стартует после перезагрузки сервера.  
- Список гостей в памяти при перезапуске сбрасывается; файл `guests.txt` в рабочей папке сохраняется между перезапусками.

Если что-то пойдёт не так, пришлите вывод `sudo systemctl status svadbabot` и последние строки `sudo journalctl -u svadbabot -n 50`.
