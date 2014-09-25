# coding=utf-8

import django.utils.translation
import django.utils.translation as translation_module
from django.utils import translation as translation_module_2
from django.utils.translation import (
    gettext as _,
    gettext_lazy as _l,
    gettext_noop as _0x90,
    ugettext as _u,
    ugettext_lazy as _ul,
    ugettext_noop as _u0x90,
    pgettext as _p,
    pgettext_lazy as _pl,
    ngettext as _n,
    ngettext_lazy as _nl,
    ungettext as _un,
    ungettext_lazy as _unl,
    npgettext as _np,
    npgettext_lazy as _npl,
)

django.utils.translation.gettext('test')
django.utils.translation.gettext_lazy('test_lazy')
django.utils.translation.gettext_noop('test_noop')
django.utils.translation.ugettext('utest')
django.utils.translation.ugettext_lazy('utest_lazy')
django.utils.translation.ugettext_noop('utest_noop')
django.utils.translation.pgettext('context', 'ptest')
django.utils.translation.pgettext_lazy('context', 'ptest_lazy')
django.utils.translation.ngettext('ntest', 'ntests', 42)
django.utils.translation.ngettext_lazy('ntest_lazy', 'ntests_lazy', 42)
django.utils.translation.ungettext('untest', 'untests', 42)
django.utils.translation.ungettext_lazy('untest_lazy', 'untests_lazy', 42)
django.utils.translation.npgettext('context', 'nptest', 'nptests', 42)
django.utils.translation.npgettext_lazy('context', 'nptest_lazy', 'nptests_lazy', 42)

translation_module.gettext('tm_test')
translation_module.gettext_lazy('tm_test_lazy')
translation_module.gettext_noop('tm_test_noop')
translation_module.ugettext('tm_utest')
translation_module.ugettext_lazy('tm_utest_lazy')
translation_module.ugettext_noop('tm_utest_noop')
translation_module.pgettext('context', 'tm_ptest')
translation_module.pgettext_lazy('context', 'tm_ptest_lazy')
translation_module.ngettext('tm_ntest', 'tm_ntests', 42)
translation_module.ngettext_lazy('tm_ntest_lazy', 'tm_ntests_lazy', 42)
translation_module.ungettext('tm_untest', 'tm_untests', 42)
translation_module.ungettext_lazy('tm_untest_lazy', 'tm_untests_lazy', 42)
translation_module.npgettext('context', 'tm_nptest', 'tm_nptests', 42)
translation_module.npgettext_lazy('context', 'tm_nptest_lazy', 'tm_nptests_lazy', 42)

translation_module_2.gettext('tm2_test')
translation_module_2.gettext_lazy('tm2_test_lazy')
translation_module_2.gettext_noop('tm2_test_noop')
translation_module_2.ugettext('tm2_utest')
translation_module_2.ugettext_lazy('tm2_utest_lazy')
translation_module_2.ugettext_noop('tm2_utest_noop')
translation_module_2.pgettext('context', 'tm2_ptest')
translation_module_2.pgettext_lazy('context', 'tm2_ptest_lazy')
translation_module_2.ngettext('tm2_ntest', 'tm2_ntests', 42)
translation_module_2.ngettext_lazy('tm2_ntest_lazy', 'tm2_ntests_lazy', 42)
translation_module_2.ungettext('tm2_untest', 'tm2_untests', 42)
translation_module_2.ungettext_lazy('tm2_untest_lazy', 'tm2_untests_lazy', 42)
translation_module_2.npgettext('context', 'tm2_nptest', 'tm2_nptests', 42)
translation_module_2.npgettext_lazy('context', 'tm2_nptest_lazy', 'tm2_nptests_lazy', 42)

_('alias_test')
_l('alias_test_lazy')
_0x90('alias_test_noop')
_u('alias_utest')
_ul('alias_utest_lazy')
_u0x90('alias_utest_noop')
_p('context', 'alias_ptest')
_pl('context', 'alias_ptest_lazy')
_n('alias_ntest', 'alias_ntests', 42)
_nl('alias_ntest_lazy', 'alias_ntests_lazy', 42)
_un('alias_untest', 'alias_untests', 42)
_unl('alias_untest_lazy', 'alias_untests_lazy', 42)
_np('context', 'alias_nptest', 'alias_nptests', 42)
_npl('context', 'alias_nptest_lazy', 'alias_nptests_lazy', 42)


def gettext(message):
    pass


gettext('not a translation')


def some_function():
    from django.utils.translation import gettext

    gettext('a translation')


gettext('still not a translation')


def something_else():
    pass


something_else().gettext('not a translation')

something = {}
something["else"].gettext('not a translation')

