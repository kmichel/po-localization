# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import collections
import io
from django import template
from django.templatetags import i18n
from django.utils import six


def extract_messages(filename, po_file, printable_filename=None):
    printable_filename = filename if printable_filename is None else printable_filename
    nodes = parse_file(filename, printable_filename)
    for lineno_node in nodes.get_nodes_by_type(LinenoNode):
        wrapped_node = lineno_node.wrapped_node
        if isinstance(wrapped_node, i18n.TranslateNode):
            message = resolve_literal_string_filter_expression(wrapped_node.filter_expression)
            if message is not None:
                context, context_is_variable = get_context_and_variability(wrapped_node)
                if not context_is_variable:
                    po_file.add_entry(message, context=context).add_location(printable_filename, lineno_node.lineno)
        elif isinstance(wrapped_node, i18n.BlockTranslateNode):
            message, singular_vars = wrapped_node.render_token_list(wrapped_node.singular)
            context, context_is_variable = get_context_and_variability(wrapped_node)
            if not context_is_variable:
                if wrapped_node.countervar and wrapped_node.counter:
                    plural, plural_vars = wrapped_node.render_token_list(wrapped_node.plural)
                    po_file.add_entry(message, plural, context).add_location(printable_filename, lineno_node.lineno)
                else:
                    po_file.add_entry(message, context=context).add_location(printable_filename, lineno_node.lineno)


def parse_file(filename, printable_filename=None):
    with io.open(filename, 'r', encoding='utf-8') as sample_file:
        file_content = sample_file.read()
    lexer = template.Lexer(file_content, printable_filename)
    tokens = lexer.tokenize()
    parser = MessageParser(tokens)
    return parser.parse()


class MessageParser(template.Parser):
    def __init__(self, tokens):
        super(MessageParser, self).__init__(tokens)
        minimal_tags = collections.defaultdict(lambda: dummy_tag)
        minimal_tags['load'] = load_i18n_tag
        minimal_tags['comment'] = self.tags['comment']
        self.tags = minimal_tags

    def find_filter(self, filter_name):
        return None

    def compile_filter(self, token):
        return MessageFilterExpression(token, self)


class MessageFilterExpression(template.FilterExpression):
    @staticmethod
    def args_check(name, func, provided):
        return True

def load_i18n_tag(parser, token):
    if token.contents.split()[1] == 'i18n':
        original_library = template.import_library('django.templatetags.i18n')
        library = template.Library()
        library.tags['trans'] = lineno_tag(original_library.tags['trans'])
        library.tags['blocktrans'] = lineno_tag(original_library.tags['blocktrans'])
        parser.add_library(library)
    return template.Node()


def dummy_tag(parser, token):
    return template.Node()


def lineno_tag(wrapped_tag):
    def wrapper(parser, token):
        return LinenoNode(token.lineno, wrapped_tag(parser, token))

    return wrapper


class LinenoNode(template.Node):
    def __init__(self, lineno, wrapped_node):
        self.lineno = lineno
        self.wrapped_node = wrapped_node


def resolve_literal_string_filter_expression(expression):
    if expression is not None:
        if len(expression.filters) == 0:
            # Sometimes a string literal appears as a SafeText and sometime as a Variable with a literal
            # This may be related to the translate option of Variable
            if isinstance(expression.var, six.text_type):
                return expression.var
            if hasattr(expression.var, 'literal') and isinstance(expression.var.literal, six.text_type):
                return expression.var.literal


def get_context_and_variability(node):
    if node.message_context is not None:
        context = resolve_literal_string_filter_expression(node.message_context)
        return context, context is None
    return None, False
