from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import io
import pandas as pd
from models import User, Tournament, Game, Event, Team, Result, UsersRank,League,EventNotification,EventRegistration
from config import Config
from extensions import db
from flask_login import login_user, LoginManager, current_user, logout_user


app = Flask(__name__)

# Настройка конфигурации приложения
app.config.from_object(Config)

# Инициализация базы данных
db.init_app(app)

# Инициализация LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Переход на страницу входа, если пользователь не аутентифицирован

# Функция для загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Страница входа
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Проверяем, существует ли пользователь
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # Аутентификация через Flask-Login
            login_user(user)
            flash('Успешный вход в систему', 'success')

            # Перенаправление в зависимости от роли
            return redirect(url_for('admin_profile') if user.role == 'admin' else url_for('user_profile'))
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('auth/login.html')

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone_number = request.form['phone']

        # Проверка на наличие уже существующего пользователя с таким логином
        if User.query.filter_by(username=username).first():
            flash('Логин уже занят', 'danger')
            return redirect(url_for('register'))

        # Проверка на наличие уже зарегистрированной почты
        if User.query.filter_by(email=email).first():
            flash('Почта уже зарегистрирована', 'danger')
            return redirect(url_for('register'))

        # Валидация пароля (например, минимальная длина)
        if len(password) < 8:
            flash('Пароль должен быть не менее 8 символов', 'danger')
            return redirect(url_for('register'))

        # Хэширование пароля
        password_hash = generate_password_hash(password)

        # Создание нового пользователя
        new_user = User(username=username, password_hash=password_hash, email=email, phone_number=phone_number)
        db.session.add(new_user)
        db.session.commit()

        # Отправка успешного сообщения
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('login'))

    return render_template('auth/register.html')



# Профиль администратора
from flask_login import login_required, current_user

@app.route('/adminprofile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    if request.method == 'POST':
        # Получаем данные из формы
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        gender = request.form.get('gender')
        phone_number = request.form.get('phone_number')
        group_num = request.form.get('group_num')

        # Проверяем уникальность логина
        if username != current_user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Этот логин уже используется. Пожалуйста, выберите другой.', 'danger')
                return redirect(url_for('admin_profile'))  # Перенаправляем на страницу профиля

        # Обновляем данные пользователя
        current_user.full_name = full_name
        current_user.username = username
        current_user.gender = gender
        current_user.phone_number = phone_number
        current_user.group_num = group_num
        print(request.form)

        # Сохраняем изменения в базе данных
        db.session.commit()

        # Показываем сообщение об успешном обновлении
        flash('Профиль успешно обновлён!', 'success')
        return redirect(url_for('admin_profile'))  # Перенаправляем на страницу профиля

    # Отображаем страницу профиля, если метод GET
    return render_template('admin/adminprofile.html', user=current_user)



@app.route('/creategame', methods=['GET', 'POST'])
@login_required
def create_game():
    leagues = League.query.all()
    users = User.query.all()
    # Получить текущую дату и время
    now = datetime.now()

    # Выбрать последние 3 непройденные игры
    upcoming_games = Game.query.filter(
        db.or_(Game.game_date > now.date(),
               db.and_(Game.game_date == now.date(), Game.game_time > now.time()))
    ).order_by(Game.game_date, Game.game_time).limit(3).all()

    if request.method == 'POST':
        # Получаем данные из формы
        topic = request.form.get('topic')
        max_participants = request.form.get('max_participants')
        game_date = request.form.get('game_date')
        game_time = request.form.get('game_time')
        location = request.form.get('location')
        league_id = request.form.get('league_id')
        judge_id = request.form.get('judge_id')

        # Проверяем, что все обязательные поля заполнены
        if not all([topic, max_participants, game_date, game_time, location, league_id, judge_id]):
            flash('Все поля обязательны!', 'danger')
            return render_template('admin/creategame.html', leagues=leagues,  user=current_user,users=users, upcoming_games=upcoming_games)

        # Преобразуем max_participants в число
        try:
            max_participants = int(max_participants)
        except ValueError:
            flash('Количество участников должно быть числом.', 'danger')
            return render_template('admin/creategame.html', leagues=leagues,  user=current_user,users=users, upcoming_games=upcoming_games)

        try:
            game_date = datetime.strptime(game_date, '%Y-%m-%d').date()
            game_time = datetime.strptime(game_time, '%H:%M').time()

            # Проверяем, что дата игры не в прошлом
            if datetime.combine(game_date, game_time) <= now:
                flash('Дата и время игры должны быть в будущем.', 'danger')
                return render_template('admin/creategame.html', leagues=leagues,  user=current_user,users=users, upcoming_games=upcoming_games)

        except ValueError:
            flash('Неверный формат даты или времени.', 'danger')
            return render_template('admin/creategame.html', leagues=leagues,  user=current_user,users=users, upcoming_games=upcoming_games)

        if not League.query.get(league_id):
            flash('Выбранная лига не существует.', 'danger')
            return render_template('admin/creategame.html', leagues=leagues,  user=current_user,users=users, upcoming_games=upcoming_games)

        if not User.query.get(judge_id):
            flash('Выбранный судья не существует.', 'danger')
            return render_template('admin/creategame.html', leagues=leagues, user=current_user, users=users, upcoming_games=upcoming_games)

        # Создаем новую игру
        new_game = Game(
            topic=topic,
            max_participants=max_participants,
            game_date=game_date,
            game_time=game_time,
            location=location,
            league_id=league_id,
            judge_id=judge_id
        )
        try:
            db.session.add(new_game)
            db.session.commit()
            print('Игра успешно создана!')
            return redirect(url_for('create_game'))  # Перенаправляем на страницу создания игры
        except Exception as e:
            db.session.rollback()
            print(f'Ошибка при создании игры: {str(e)}')

    return render_template('admin/creategame.html', leagues=leagues,  user=current_user,users=users, upcoming_games=upcoming_games)

@app.route('/deletegame/<int:game_id>', methods=['POST'])
@login_required
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    try:
        db.session.delete(game)
        db.session.commit()
        return jsonify({'message': 'Игра успешно удалена!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ошибка при удалении игры: {str(e)}'}), 500

@app.route('/updategame/<int:game_id>', methods=['PUT', 'PATCH'])
@login_required
def update_game(game_id):
    game = Game.query.get_or_404(game_id)
    data = request.json

    game.topic = data.get('topic', game.topic)
    game.max_participants = data.get('max_participants', game.max_participants)
    game.game_date = datetime.strptime(data.get('game_date', game.game_date.strftime('%Y-%m-%d')), '%Y-%m-%d').date()
    game.game_time = datetime.strptime(data.get('game_time', game.game_time.strftime('%H:%M')), '%H:%M').time()
    game.location = data.get('location', game.location)

    try:
        db.session.commit()
        return jsonify({'message': 'Игра успешно обновлена!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ошибка при обновлении игры: {str(e)}'}), 500


@app.route('/usermanage')
@login_required
def user_manage():
    # Извлекаем всех пользователей из базы данных
    users = User.query.all()
    return render_template('admin/usermanage.html', users=users, user=current_user)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user_manage'))

@app.route('/change_rank/<int:user_id>', methods=['POST'])
@login_required
def change_rank(user_id):
    new_rank = request.form['new_rank']

    # Обновляем ранг пользователя
    rank = UsersRank.query.filter_by(user_id=user_id).first()
    if rank:
        rank.rank_name = new_rank
        db.session.commit()
        flash('Ранг обновлен успешно!', 'success')
    else:
        flash('Пользователь не найден!', 'danger')

    return redirect(url_for('user_manage'))


@app.route('/newevent', methods=['GET', 'POST'])
@login_required
def new_event():
    now = datetime.now()

    # Получаем список событий
    events = Event.query.filter(Event.event_date >= now.date()).order_by(Event.event_date).all()

    if request.method == 'POST':
        action = request.form.get('action')  # Действие: delete или stop
        event_id = request.form.get('event_id')  # ID события

        # Проверка на удаление
        if action == 'delete' and event_id:
            event = Event.query.get(event_id)
            if event:
                try:
                    db.session.delete(event)
                    db.session.commit()
                    flash('Событие успешно удалено.', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Ошибка при удалении события: {str(e)}', 'danger')
            else:
                flash('Событие не найдено.', 'danger')

            return redirect(url_for('new_event'))

        # Проверка на остановку регистрации
        if action == 'stop' and event_id:
            event = Event.query.get(event_id)
            if event:
                try:
                    event.is_stopped = True
                    db.session.commit()
                    flash('Регистрация на событие остановлена.', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Ошибка при остановке регистрации: {str(e)}', 'danger')
            else:
                flash('Событие не найдено.', 'danger')

            return redirect(url_for('new_event'))

       # Логика создания нового события
        topic = request.form.get('topic')
        description = request.form.get('discription')  # Проверьте правильность названия 'discription'
        game_date = request.form.get('event_date')
        game_time = request.form.get('event_time')
        location = request.form.get('location')
        created_by = int(request.form.get('created_by'))  # Преобразуйте в целое число

        if not all([topic, description, game_date, game_time, location, created_by]):
            flash('Все поля обязательны!', 'danger')
            return render_template('admin/newevent.html', user=current_user, events=events)

        # Проверяем, существует ли пользователь с таким ID
        user = User.query.get(created_by)
        if not user:
            flash('Пользователь с таким ID не найден.', 'danger')
            return render_template('admin/newevent.html', events=events, user=current_user)

        # Обработка даты и времени
        try:
            event_date = datetime.strptime(game_date, '%Y-%m-%d').date()
            event_time = datetime.strptime(game_time, '%H:%M').time()
        except ValueError:
            flash('Неверный формат даты или времени.', 'danger')
            return render_template('admin/newevent.html', events=events, user=current_user)

        # Создание нового события
        new_game = Event(
            name=topic,
            description=description,
            event_date=event_date,
            event_time=event_time,
            location=location,
            created_by=created_by,
        )
        print(new_game)  # Для отладки
        db.session.add(new_game)
        db.session.commit()
        return redirect(url_for('new_event'))


    return render_template('admin/newevent.html', events=events, user=current_user)


# Страница отчета
@app.route('/adminreports', methods=['GET'])
@login_required
def admin_report():
    return render_template('admin/adminreports.html',user=current_user)


#------- роуты для пользователя ------


@app.route('/userprofile', methods=['GET', 'POST'])
@login_required  # Требуется авторизация
def user_profile():
    if request.method == 'POST':
        # Получаем данные из формы
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        gender = request.form.get('gender')
        phone_number = request.form.get('phone_number')
        group_num = request.form.get('group_num')

        # Проверяем уникальность логина
        if username != current_user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Этот логин уже используется. Пожалуйста, выберите другой.', 'danger')
                return redirect(url_for('user_profile'))  # Перенаправляем на страницу профиля

        # Обновляем данные пользователя
        current_user.full_name = full_name
        current_user.username = username
        current_user.gender = gender
        current_user.phone_number = phone_number
        current_user.group_num = group_num
        print(request.form)

        # Сохраняем изменения в базе данных
        db.session.commit()

        # Показываем сообщение об успешном обновлении
        flash('Профиль успешно обновлён!', 'success')
        return redirect(url_for('user_profile'))  # Перенаправляем на страницу профиля

    # Отображаем страницу профиля, если метод GET
    return render_template('user/userprofile.html', user=current_user)


# Страница создания команд
@app.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():
    users = User.query.all()
    if request.method == 'POST':
        # Получение данных из формы
        team_name = request.form['team_name']
        participants_count = int(request.form['participants'])  # Преобразуем в число
        speaker_1_id = int(request.form.get('speaker_1')) if request.form.get('speaker_1') else None  # Преобразуем в число или None
        speaker_2_id = int(request.form.get('speaker_2')) if request.form.get('speaker_2') else None  # Преобразуем в число или None

        # Создание новой команды с участниками и спикерами
        new_team = Team(
            name=team_name,
            participants_count=participants_count,
            speaker_1=speaker_1_id,
            speaker_2=speaker_2_id
        )
        db.session.add(new_team)
        db.session.commit()

        flash('Команда успешно создана!', 'success')
        return redirect(url_for('create_team'))
    return render_template('user/createteams.html', user=current_user,users=users)

# Маршрут для отображения списка мероприятий
@app.route('/user_events', methods=['GET', 'POST'])
@login_required
def events():
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        event = Event.query.get(event_id)
        if not event:
            flash('Мероприятие не найдено.', 'danger')
            return redirect(url_for('user_events'))

        # Проверка, зарегистрирован ли пользователь
        existing_registration = EventRegistration.query.filter_by(
        event_id=event_id, user_id=current_user.user_id
        ).first()
        if existing_registration:
            flash('Вы уже зарегистрированы на это мероприятие.', 'warning')
            return redirect(url_for('user_events'))

        # Добавление регистрации
        registration = EventRegistration(
            event_id=event_id,
            user_id=current_user.id,
            team_id=None  # При необходимости добавьте логику для команды
        )
        db.session.add(registration)
        db.session.commit()
        flash('Вы успешно зарегистрировались на мероприятие.', 'success')
        return redirect(url_for('user_events'))

    # Получение списка мероприятий
    events = Event.query.filter_by(is_stopped=False).all()
    return render_template('user/events.html', events=events,user = current_user)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5000')