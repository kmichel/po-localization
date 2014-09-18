# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls import url
from .views import test_view

urlpatterns = [
    url(r'^$', test_view)
]
