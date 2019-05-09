import os
import functools
from datetime import datetime

from flask import Blueprint, abort, session, g, request, jsonify, current_app, send_from_directory
from werkzeug.security import check_password_hash
from werkzeug.contrib.cache import SimpleCache

from ubattery.db import get_db

bp = Blueprint('auth', __name__)


def login_required(view):
    """用户登录以后才能进行相关操作。
    在每个视图中可以使用 装饰器 来完成这个工作。
    装饰器返回一个新的视图，该视图包含了传递给装饰器的原视图。
    新的函数检查用户 是否已载入。
    如果已载入，那么就继续正常执行原视图，否则就重定向到登录页面。
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            abort(403)

        return view(**kwargs)

    return wrapped_view


def super_user_required(view):
    """只有超级管理员才能操作
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            abort(403)
        user_type = g.user[1]
        if user_type != 1:  # 不是超级管理员
            abort(403)

        return view(**kwargs)

    return wrapped_view


# 用于缓存用户信息
user_cache = SimpleCache()

# bp.before_app_request 注册一个在视图函数之前运行的函数，不论其 URL 是什么。
# before_app_request 全局的
# before_request 是当前蓝图的
@bp.before_app_request
def load_logged_in_user():
    """load_logged_in_user 检查用户 id 是否已经储存在 session 中，
    并从数据库中获取用户数据，然后储存在 g.user 中。
    g.user 的持续时间比请求要长。
    如果没有用户 id ，或者 id 不存在，那么 g.user 将会是 None 。
    """

    user_name = session.get('user_name')

    if user_name is None:
        g.user = None
    else:
        g.user = user_cache.get(user_name)
        if g.user is None:
            with get_db().cursor() as cursor:
                cursor.execute(
                    'SELECT user_name, user_type FROM users WHERE user_name = %s LIMIT 1', (user_name,)
                )

                g.user = cursor.fetchone()

            if g.user is not None:
                user_cache.set(user_name, g.user)


@bp.route('/login', methods=('GET', 'POST'))
def login():

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if request.method == 'GET':
        user_name = session.get('user_name')

        if user_name is None:
            return jsonify({
                'status': False,
                'data': None
            })

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT '
                'password, '
                'id, '
                'user_name, '
                'user_type, '
                'avatar_name, '
                'DATE_FORMAT(last_login_time, \'%%Y-%%m-%%d %%H:%%i:%%s\'), '
                'user_status '
                'FROM users WHERE user_name = %s LIMIT 1',
                (user_name,)
            )
            user_info = cursor.fetchone()

            error = None
            if user_info is None:
                error = 'cookie 获取失败！'
            elif user_info[6] == 0:
                error = '该用户已被禁止登录！'

            if error:
                return jsonify({
                    'status': False,
                    'data': error
                })

    else:
        data = request.get_json()
        user_name = data['userName']

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT '
                'password, '
                'id, '
                'user_name, '
                'user_type, '
                'avatar_name, '
                'DATE_FORMAT(last_login_time, \'%%Y-%%m-%%d %%H:%%i:%%s\'), '
                'user_status '
                'FROM users WHERE user_name = %s LIMIT 1',
                (user_name,)
            )
            user_info = cursor.fetchone()

            error = None
            if user_info is None:
                error = '帐号或密码错误！'
            # check_password_hash() 以相同的方式哈希提交的密码并安全的比较哈希值。
            # 如果匹配成功，那么密码就是正确的。
            elif not check_password_hash(user_info[0], data['password']):
                error = '帐号或密码错误！'
            elif user_info[6] == 0:
                error = '该用户已被禁止登录！'

            if error:
                return jsonify({
                    'status': False,
                    'data': error
                })

            cursor.execute(
                'UPDATE users SET '
                'last_login_time = %s, '          # 更新最后登录时间
                'login_count = login_count + 1 '  # 登录次数加 1
                'WHERE user_name = %s',
                (now, user_name)
            )
            db.commit()

    # session 是一个 dict ，它用于储存横跨请求的值。
    # 当验证 成功后，用户的 id 被储存于一个新的会话中。
    # 会话数据被储存到一个 向浏览器发送的 cookie 中，在后继请求中，浏览器会返回它。
    # Flask 会安全对数据进行 签名 以防数据被篡改。
    # 默认存活时间为到浏览器关闭
    session.clear()
    # 现在用户的 id 已被储存在 session 中，可以被后续的请求使用。
    # 请每个请求的开头，如果用户已登录，那么其用户信息应当被载入，以使其可用于其他视图。
    session['user_name'] = user_info[2]

    # TODO 返回时要注意数据顺序，别把重要数据返回了
    return jsonify({
        'status': True,
        'data': {
            'userName': user_info[2],
            'userType': user_info[3],
            'avatarName': user_info[4],
            'lastLoginTime': user_info[5]
        }
    })


@bp.route('/logout')
@login_required
def logout():
    """注销的时候需要把用户 id 从 session 中移除。
    然后 load_logged_in_user 就不会在后继请求中载入用户了。
    """

    session.clear()

    return jsonify({
        'status': True,
        'data': None
    })


@bp.route('/media/avatars/<string:filename>')
@login_required
def get_avatar(filename):
    """获取用户头像"""

    base_dir = os.path.join(current_app.instance_path, current_app.config['AVATAR_PATH'])

    return send_from_directory(base_dir, filename)