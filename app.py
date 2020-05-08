from sanic import Sanic, response
from sanic_jinja2 import SanicJinja2

from sanic_auth import Auth

from database import Database

import bcrypt
import aiohttp
import io

app = Sanic(__name__)
app.config.AUTH_LOGIN_ENDPOINT = 'login'

auth = Auth(app)

jinja = SanicJinja2(app)

db = Database()

session = {}

app.static(uri='/static', name='static', file_or_directory='./static')


@app.middleware('request')
async def add_session(request):
    request['session'] = session


@app.route('/register', methods=['GET', 'POST'])
@jinja.template('register.html')
async def register(request):

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        password_repeat = request.form.get('passwordRepeat')

        if password == password_repeat:

            password_hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

            user = db.create_user(username, password_hashed.decode())
            auth.login_user(request, user)

            return response.json({
                'redirect': True,
                'redirect_url': '/'
            })
        else:
            return response.json({'message_error': 'Password mismatch. Try again.'})

    return {}


@app.route('/login', methods=['GET', 'POST'])
@jinja.template('login.html')
async def login(request):

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        user = db.check_user(username)

        if user is None:
            return response.json({
                'message_error': 'A user with this combination of username and password does not exist. '
                                 'Check that the data entered is correct.'
            })

        if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            auth.login_user(request, user)
            return response.json({
                'redirect': True,
                'redirect_url': '/'
            })
        else:
            return response.json({
                'message_error': 'Password invalid.'
            })

    return {}


@app.route('/logout')
@auth.login_required
async def logout(request):
    auth.logout_user(request)
    return response.redirect('/')


@app.route('/')
@auth.login_required(user_keyword='user')
@jinja.template('table_links.html')
async def table_main(request, user):
    links = db.get_links(user.id)
    return {
        'username': user.name,
        'links': links
    }


# Дисскуссию на тему POST/PUT/DEL можем провести.
# Но на самом деле я не вижу принципиальной разницы.
# Хотя согласен что так делать не совсем правильно.
# У скольких людей спрашивал, все говорили
# (в том числе и довольно опытные разработчики) что на это плюс минус пофиг в домашних приложениях.
# Однако при разработке rest api для, например, для мобильного приложения,
# все таки лучше использовать выше упомянутые методы запросов, а все ниже описанные функции обрамлять в одну
# и сортировать логику обработки данных и выдаче ответа по методу запроса.
# Но я сделал на постах и в разных функция потому что, почему бы и нет.
@app.route('/download_link')
@auth.login_required(user_keyword='user')
async def download_link(request, user):

    id_link = request.args.get('id')

    link = db.get_link(id_link)

    if link is None:
        return response.json({
            'message_error': 'link does not exists or cant downloadable'
        })
    else:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(link['url'], ssl=True) as resp:
                data = await resp.read()
                b_io = io.BytesIO(data)
                return response.raw(b_io.getvalue(),
                                    headers={"Content-Disposition": 'attachment; filename="{}"'.format(link['name'])})


@app.route('/create_link', methods=["POST"])
@auth.login_required(user_keyword='user')
async def create_link(request, user):

    if 'name' not in request.form or 'url' not in request.form:
        return response.json({
            'message_error': 'Send all information for create link'
        })

    link_name = request.form.get('name')
    link_url = request.form.get('url')

    if db.create_link(link_name, link_url, user.id):
        return response.json({
            'redirect': True,
            'redirect_url': '/'
        })


@app.route('/delete_link', methods=["POST"])
@auth.login_required
async def delete_link(request):

    id_link = request.args.get('id')

    if db.delete_link(id_link):
        return response.json({
            'redirect': True,
            'redirect_url': '/'
        })
    else:
        return response.json({
            'message_error': 'Failed to delete link. Try again.'
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
