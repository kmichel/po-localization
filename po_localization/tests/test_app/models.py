# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class TestModel(models.Model):
    test_field = models.TextField(verbose_name=_('test field'))
