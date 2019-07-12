from flask import Blueprint, render_template, send_from_directory, current_app

from ubattery.extensions import cache

# Blueprint 是一种组织一组相关视图及其他代码的方式。
# 与把视图及其他 代码直接注册到应用的方式不同，
# 蓝图方式是把它们注册到蓝图，然后在工厂函数中 把蓝图注册到应用。
# 这里创建了一个名称为 'auth' 的 Blueprint 。
# 和应用对象一样， 蓝图需要知道是在哪里定义的，因此把 __name__ 作为函数的第二个参数。
# url_prefix 会添加到所有与该蓝图关联的 URL 前面。
index_bp = Blueprint('index', __name__)


@index_bp.route('/')
@cache.cached()
def index():
    return render_template('index.html')


@index_bp.route('/favicon.ico')
def favicon():
    """获取网页图标。"""

    return send_from_directory(current_app.template_folder, 'favicon.ico')


@index_bp.route('/media/avatars/<string:filename>')
def get_avatar(filename):
    """获取用户头像。"""

    return send_from_directory(current_app.avatar_folder, filename)