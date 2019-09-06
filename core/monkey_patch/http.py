# -*- coding: utf-8 -*-
import os
import math
import random
import jinja2
import odoo

from odoo import http
from odoo.addons.web import controllers

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

# 更改数据库页面
# 添加数据库主页logo随机数
path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'hh_addons/hh_base/template'))
loader = jinja2.FileSystemLoader(path)
env = jinja2.Environment(loader=loader, autoescape=True)


db_monodb = http.db_monodb
DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'


def _render_template(self, **d):
    d.setdefault('manage',True)
    d['insecure'] = odoo.tools.config['admin_passwd'] == 'admin'
    d['list_db'] = odoo.tools.config['list_db']
    d['langs'] = odoo.service.db.exp_list_lang()
    d['countries'] = odoo.service.db.exp_list_countries()
    d['pattern'] = DBNAME_PATTERN
    d['databases'] = []
    #添加随机数
    d['random_number'] = str(int(math.ceil(random.random() * 100000)))
    try:
        d['databases'] = http.db_list()
    except odoo.exceptions.AccessDenied:
        monodb = db_monodb()
        if monodb:
            d['databases'] = [monodb]
    return env.get_template("database_manager.html").render(d)


def patch_http():

    # 配置系统参数
    controllers.main.Database._render_template = _render_template
