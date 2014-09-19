# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import ast
import io

GETTEXT_FUNCTIONS = ('gettext', 'gettext_lazy', 'gettext_noop', 'ugettext', 'ugettext_lazy', 'ugettext_noop')
PGETTEXT_FUNCTIONS = ('pgettext', 'pgettext_lazy')
NGETTEXT_FUNCTIONS = ('ngettext', 'ungettext', 'ngettext_lazy', 'ungettext_lazy')
NPGETTEXT_FUNCTIONS = ('npgettext', 'npgettext_lazy')


def extract_messages(filename, po_file, printable_filename=None):
    printable_filename = filename if printable_filename is None else printable_filename
    with io.open(filename, mode='rb') as python_file:
        file_content = python_file.read()
    tree = ast.parse(file_content, printable_filename)
    extractor = PythonExtractor(printable_filename, po_file)
    extractor.visit(tree)


class PythonExtractor(ast.NodeVisitor):
    def __init__(self, filename, po_file):
        self.filename = filename
        self.aliases = ScopedAliases()
        self.po_file = po_file

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == 'django.utils.translation':
                self._add_function_aliases_for_module(alias)

    def visit_ImportFrom(self, node):
        if node.level == 0:
            if node.module == 'django.utils.translation':
                for alias in node.names:
                    visible_name = alias.name if alias.asname is None else alias.asname
                    if alias.name in GETTEXT_FUNCTIONS:
                        self.aliases.set(visible_name, 'gettext')
                    elif alias.name in PGETTEXT_FUNCTIONS:
                        self.aliases.set(visible_name, 'pgettext')
                    elif alias.name in NGETTEXT_FUNCTIONS:
                        self.aliases.set(visible_name, 'ngettext')
                    elif alias.name in NPGETTEXT_FUNCTIONS:
                        self.aliases.set(visible_name, 'npgettext')
            elif node.module == 'django.utils':
                for alias in node.names:
                    if alias.name == 'translation':
                        self._add_function_aliases_for_module(alias)

    def _add_function_aliases_for_module(self, module_alias):
        visible_name = module_alias.name if module_alias.asname is None else module_alias.asname
        for function in GETTEXT_FUNCTIONS:
            self.aliases.set(visible_name + '.' + function, 'gettext')
        for function in PGETTEXT_FUNCTIONS:
            self.aliases.set(visible_name + '.' + function, 'pgettext')
        for function in NGETTEXT_FUNCTIONS:
            self.aliases.set(visible_name + '.' + function, 'ngettext')
        for function in NPGETTEXT_FUNCTIONS:
            self.aliases.set(visible_name + '.' + function, 'npgettext')

    def visit_FunctionDef(self, node):
        self.aliases = ScopedAliases(self.aliases)
        self.generic_visit(node)
        self.aliases = self.aliases.parent_scope

    def visit_Call(self, node):
        function_name = _get_dotted_name(node.func)
        aliased_name = self.aliases.get(function_name)
        if aliased_name is not None:
            entry = None
            # XXX: args could be passed in *args, **kwargs or as keywords
            if aliased_name == 'gettext' and _first_args_are_strings(node.args, 1):
                entry = self.po_file.add_entry(message=node.args[0].s)
            elif aliased_name == 'pgettext' and _first_args_are_strings(node.args, 2):
                entry = self.po_file.add_entry(context=node.args[0].s, message=node.args[1].s)
            elif aliased_name == 'ngettext' and _first_args_are_strings(node.args, 1):
                entry = self.po_file.add_entry(message=node.args[0].s, plural=node.args[1].s)
            elif aliased_name == 'npgettext' and _first_args_are_strings(node.args, 2):
                entry = self.po_file.add_entry(context=node.args[0].s, message=node.args[1].s, plural=node.args[2].s)
            if entry:
                entry.add_location(self.filename, node.lineno)
        self.generic_visit(node)

    # The rest of the code is here only for performances reasons
    # you can remove it and keep exactly the same visible behavior.

    # These are sorted by frequency
    IGNORED_CLASSES = (ast.Name, str, ast.Load, ast.Str, ast.Num, bool)

    def generic_visit(self, node):
        for field in node._fields:
            value = getattr(node, field)
            if value.__class__ is list:
                for item in value:
                    if item is not None and item.__class__ not in self.IGNORED_CLASSES:
                        self.visit(item)
            elif value is not None and value.__class__ not in self.IGNORED_CLASSES:
                self.visit(value)

    def visit(self, node):
        cls = node.__class__
        if cls is ast.Call:
            self.visit_Call(node)
        elif cls is ast.Import:
            self.visit_Import(node)
        elif cls is ast.ImportFrom:
            self.visit_ImportFrom(node)
        elif cls is ast.FunctionDef:
            self.visit_FunctionDef(node)
        else:
            self.generic_visit(node)


class ScopedAliases(object):
    def __init__(self, parent_scope=None):
        self.aliases = {}
        self.parent_scope = parent_scope

    def get(self, name):
        aliased_name = self.aliases.get(name, None)
        if aliased_name is None and self.parent_scope is not None:
            return self.parent_scope.get(name)
        else:
            return aliased_name

    def set(self, name, aliased_name):
        self.aliases[name] = aliased_name


def _first_args_are_strings(args, length):
    return len(args) >= length and all(isinstance(arg, ast.Str) for arg in args[:length])


def _get_dotted_name(node, suffix=''):
    if isinstance(node, ast.Name):
        return node.id + suffix
    elif isinstance(node, ast.Attribute):
        return _get_dotted_name(node.value, '.' + node.attr + suffix)
    else:
        return None
