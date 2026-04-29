# Deploy на VPS (Nginx + Gunicorn + systemd + HTTPS) для домена цветы.online

Домен в punycode: `xn--b1ag3bn2a.online`.

## 0) Требования
- Ubuntu 22.04/24.04
- Открыты порты 22, 80, 443

## 1) Установка пакетов
```bash
sudo apt update && sudo apt -y upgrade
sudo apt -y install python3-venv python3-pip nginx ufw fail2ban postgresql postgresql-contrib
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## 2) PostgreSQL
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE atrium;
CREATE USER atrium_user WITH PASSWORD 'STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE atrium TO atrium_user;
\q
```

## 3) Код проекта
Распакуй проект в `/home/atrium/app`.

```bash
sudo adduser atrium
sudo usermod -aG sudo atrium
```

## 4) Python окружение и зависимости
```bash
cd /home/atrium/app
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 5) .env
Скопируй пример и заполни:
```bash
cp .env.example .env
nano .env
```
Важно: выстави
- `DJANGO_DEBUG=0`
- `DJANGO_ALLOWED_HOSTS=цветы.online,xn--b1ag3bn2a.online,www.цветы.online,www.xn--b1ag3bn2a.online`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://цветы.online,https://xn--b1ag3bn2a.online,https://www.цветы.online,https://www.xn--b1ag3bn2a.online`
- `DATABASE_URL=postgres://atrium_user:STRONG_PASSWORD@127.0.0.1:5432/atrium`

## 6) Django миграции и статика
```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

## 7) systemd сервисы
Скопируй файлы:
```bash
sudo cp deploy/vps/systemd_atrium-web.service /etc/systemd/system/atrium-web.service
sudo cp deploy/vps/systemd_atrium-bot.service /etc/systemd/system/atrium-bot.service
```
Отредактируй пути при необходимости (WorkingDirectory).

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now atrium-web
sudo systemctl enable --now atrium-bot
sudo systemctl status atrium-web --no-pager
sudo systemctl status atrium-bot --no-pager
```

## 8) Nginx
```bash
sudo cp deploy/vps/nginx_cvety.online.conf /etc/nginx/sites-available/cvety.online
sudo ln -sf /etc/nginx/sites-available/cvety.online /etc/nginx/sites-enabled/cvety.online
sudo nginx -t
sudo systemctl reload nginx
```

## 9) HTTPS (Let's Encrypt)
```bash
sudo apt -y install certbot python3-certbot-nginx
sudo certbot --nginx -d цветы.online -d www.цветы.online -d xn--b1ag3bn2a.online -d www.xn--b1ag3bn2a.online
```

## 10) Логи
```bash
journalctl -u atrium-web -f
journalctl -u atrium-bot -f
```
