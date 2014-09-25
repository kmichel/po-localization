# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from django.http import HttpResponse
from django.utils.translation import ugettext as _


def test_view(request):
    return HttpResponse(_('test project string'))
