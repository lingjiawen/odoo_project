# -*- coding: utf-8 -*-

from core.monkey_patch.http import patch_http


def monkey_patch():
    patch_http()
