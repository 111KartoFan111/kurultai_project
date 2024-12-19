# kurultai_project
```
my_flask_app/
├── app.py                     Главный файл приложения
├── config.py                  Настройки приложения
├── extensions.py              Подключение расширений (SQLAlchemy)
├── models.py                  ORM-модели для базы данных
├── templates/                 Шаблоны (рендеринг на сервере)
│   ├── auth/
│   │   ├── login.html         Страница входа
│   │   ├── register.html      Страница регистрации
│   ├── admin/                 Шаблоны для админ панели
│   │   ├── apminprofile.html     Панель администратора
│   │   ├── newgame.html       Создание игры
│   │   ├── usermanage.html    Управление пользователями
│   │   ├── newevent.html      Создание мероприятия
│   │   ├── adminreports.html  Отчеты
│   ├── user/                  Шаблоны для пользовательской панели
│   │   ├── userprofile.html       Личный кабинет пользователя
│   │   ├── newcommand.html    Создание команды
│   │   ├── events.html        Список мероприятий
│   │   ├── userreports.html   Отчеты
├── static/                    Статические файлы (CSS, JS, изображения)
│   ├── css/
│   │   ├── login.css  Стили для страницы входа
│   │   ├── login.css  Стили для страницы регистрации
│   │   ├── admin/             Стили для админ панели
│   │   │   ├── adminprofile.css  Стили для страницы панели администратора
│   │   │   ├── newgame.css    Стили для страницы создания игры
│   │   │   ├── usermanage.css  Стили для страницы управления пользователями
│   │   │   ├── newevent.css   Стили для страницы создания мероприятия
│   │   │   ├── adminreports.css    Стили для страницы отчетов
│   │   ├── user/              Стили для пользовательской панели
│   │   │   ├── userprofile.css    Стили для страницы профиля пользователя
│   │   │   ├── teams.css     Стили для страницы создания команды
│   │   │   ├── events.css         Стили для страницы мероприятий
│   │   │   └── reports.css        Стили для страницы отчетов
│   ├── img/                   Изображения
├── README.md                  Документация
├── requirements.txt           Зависимости Python
```
