# 1. Берем готовый официальный образ веб-сервера Nginx
FROM nginx:alpine

# 2. Копируем наш файл index.html внутрь папки, откуда Nginx раздает сайты
COPY index.html /usr/share/nginx/html/index.html
