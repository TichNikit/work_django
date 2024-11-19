import time

from django.db import transaction
from django.shortcuts import render, redirect
from django.http import HttpResponse

from task.models import *


# Create your views here.
def welcome(request):
    '''
    Функция переводит пользователя на главный экран приложения.
    '''
    return render(request, 'welcome.html')

def regist_user(request):
    '''
    Функция возвращает форму для регистрации пользователя.
    Если запрос отправлен методом POST, функция обрабатывает информацию, полученную при регистрации пользователя,
    и добавляет её в базу данных.
    Если логин уже есть в базе данных, то выводится ошибка и сообщение "Логин уже занят((( Попробуйте другой"
    '''
    users = User.objects.all()
    users_list = [user.username for user in users]

    if request.method == 'POST':
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        password = request.POST.get('password')

        if username not in users_list:
            user = User.objects.create(username=username, firstname=firstname,lastname=lastname,password=password)
            context = {
                'username': username,
                'user_id': user.id,
            }
            return render(request, 'welcome_user.html', context=context)
        else:
            return HttpResponse(f'Логин уже занят((( Попробуйте другой')
    return render(request, 'regist_user.html')


def get_list_user(request):
    '''
    Функция возвращает список зарегистрированных пользователей.
    '''
    users = User.objects.all()
    context = {
        'users_list': users,
    }
    return render(request, 'list_user.html', context)


def get_list_game(request):
    '''
    Функция возвращает список игр.
    '''
    games = Game.objects.all()
    context = {
        'game_list': games,
    }
    return render(request, 'list_game.html', context)



def get_game(request, game_id: int):
    '''
    Функция возвращает информацию о конкретной игре.
    '''
    game = Game.objects.filter(id=game_id).first()
    if not game:
        return render(request, '404.html', status=404)

    ratings = Rating.objects.select_related('user').filter(game_id=game_id).all()
    feedbacks = Feedback.objects.select_related('user').filter(game_id=game_id).all()

    return render(request, 'game.html', {
        'game': game,
        'ratings': ratings,
        'feedbacks': feedbacks,
        'game_id': game.id,
    })


def get_user(request, user_id: int):
    '''
    Функция возвращает информацию о конкретном пользователе.
    '''
    user = User.objects.filter(id=user_id).first()
    if not user:
        return render(request, '404.html', status=404)

    ratings = Rating.objects.select_related('game').filter(user_id=user_id).all()
    feedbacks = Feedback.objects.select_related('game').filter(user_id=user_id).all()

    return render(request, 'user.html', {
        'user': user,
        'ratings': ratings,
        'feedbacks': feedbacks,
    })


#Добавить оценку____________________________________________________________________________________________

def check_rating_entry(request):
    '''
    Функция возвращает форму для проверки налиция регистрации у пользователя.
    Если запрос отправлен методом POST, функция обрабатывает информацию, полученную при проверки пользователя на наличие
    регистрации.
    Если id пользователя нет в базе данных, то выводится надпись:"Пользователь не найден -_-\nПопробуйте снова"
    Если введенные данные не совпадаю с теми, что записаны в базе данных, то выводится ошибка с надписью:
    "Что-то пошло не так ((\nПопробуйте снова"
    '''
    global global_user
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_id = request.POST.get('user_id')

        user = User.objects.filter(id=user_id).first()
        if not user:
            error = 'Пользователь не найден -_-\nПопробуйте снова'
            return render(request, 'rating_entry.html', {'error': error})

        if username == user.username and password == user.password:
            global_user = user
            return redirect('rating/')
        else:
            error = 'Что-то пошло не так ((\nПопробуйте снова'
            return render(request, 'rating_entry.html', {'error': error})

    return render(request, 'rating_entry.html')


def rating_finish(request):
    '''
    Функция возвращает форму для оставления оценки.
    Если запрос отправлен методом POST, функция обрабатывает информацию, полученную от пользователя при оставлении оценки.
    Если оценка у пользователя к игре уже есть, то оценка будет отредактирован.
    Если id игры нет в базе данные, выводится ошибка с надписью "Game not found".
    Если оценка выйдет из диапазона 0-10, то выведится ошибка.
    '''
    if request.method == 'POST':
        rating_int = request.POST.get('rating_int')
        game_id = request.POST.get('game_id')
        user_id = global_user.id if global_user else None

        if user_id is None:
            return HttpResponse("User not found")

        game = Game.objects.filter(id=game_id).first()
        if game is None:
            return HttpResponse("Game not found")
        if int(rating_int) > 10:
            return HttpResponse("More 10")
        if int(rating_int) < 0:
            return HttpResponse("Less 10")
        with transaction.atomic():
            existing_rating = Rating.objects.filter(user_id=user_id, game_id=game_id).first()
            if existing_rating is not None:
                existing_rating.score = rating_int
                existing_rating.save()
            else:
                Rating.objects.create(user_id=user_id, game_id=game_id, score=rating_int)
        return render(request, 'finish_feedback.html')

    return render(request, 'rating.html')

#Добавить отзыв_________________________________________________________________________________________________________

def check_feedback_entry(request):
    '''
    Функция возвращает форму для проверки налиция регистрации у пользователя.
    Если запрос отправлен методом POST, функция обрабатывает информацию, полученную при проверки пользователя на наличие
    регистрации.
    Если id пользователя нет в базе данных, то выводится надпись:"Пользователь не найден -_-\nПопробуйте снова"
    Если введенные данные не совпадаю с теми, что записаны в базе данных, то выводится ошибка с надписью:
    "Что-то пошло не так ((\nПопробуйте снова"
    '''
    global global_user
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_id = request.POST.get('user_id')

        user = User.objects.filter(id=user_id).first()
        if not user:
            error = 'Пользователь не найден -_-\nПопробуйте снова'
            return render(request, 'rating_entry.html', {'error': error})

        if username == user.username and password == user.password:
            global_user = user
            return redirect('feedback/')
        else:
            error = 'Что-то пошло не так ((\nПопробуйте снова'
            return render(request, 'feedback_entry.html', {'error': error})

    return render(request, 'feedback_entry.html')


def feedback_finish(request):
    '''
    Функция возвращает форму для оставления отзыва к игре.
    Если запрос отправлен методом POST, функция обрабатывает информацию, полученную от пользователя при оставлении отзыва.
    Если отзыв у пользователя к игре уже есть, то отзыв будет отредактирован.
    Если id игры нет в базе данные, выводится ошибка с надписью "Game not found".
    '''
    if request.method == 'POST':
        feedback_user = request.POST.get('feedback_user')
        game_id = request.POST.get('game_id')
        user_id = global_user.id if global_user else None

        if user_id is None:
            return HttpResponse("User not found")

        game = Game.objects.filter(id=game_id).first()
        if game is None:
            return HttpResponse("Game not found")

        with transaction.atomic():
            existing_feedback = Feedback.objects.filter(user_id=user_id, game_id=game_id).first()
            if existing_feedback is not None:
                existing_feedback.feedback_user = feedback_user
                existing_feedback.save()
            else:
                Feedback.objects.create(user_id=user_id, game_id=game_id, feedback_user=feedback_user)
        return render(request, 'finish_feedback.html')

    return render(request, 'feedback.html')