import argparse
import collections
import io
import sys
import ast
from tokenize_rt import ESCAPED_NL
from tokenize_rt import Offset
from tokenize_rt import src_to_tokens
from tokenize_rt import Token
from tokenize_rt import tokens_to_src
from tokenize_rt import UNIMPORTANT_WS

Call = collections.namedtuple('Call', ('node', 'star_args', 'arg_offsets'))
Func = collections.namedtuple('Func', ('node', 'star_args', 'arg_offsets'))
Class = collections.namedtuple('Class', ('node', 'star_args', 'arg_offsets'))
Literal = collections.namedtuple('Literal', ('node', ))
Fix = collections.namedtuple('Fix', ('braces', 'multi_arg', 'initial_indent'))

NEWLINES = frozenset((ESCAPED_NL, 'NEWLINE', 'NL'))
NON_CODING_TOKENS = frozenset(('COMMENT', ESCAPED_NL, 'NL', UNIMPORTANT_WS))
INDENT_TOKENS = frozenset(('INDENT', UNIMPORTANT_WS))
START_BRACES = frozenset(('(', '{', '['))
END_BRACES = frozenset((')', '}', ']'))


def ast_parse(contents_text):
    return ast.parse(contents_text.encode('UTF-8'))


def _to_offset(node):
    candidates = [node]
    while candidates:
        candidate = candidates.pop()
        if hasattr(candidate, 'lineno'):
            return Offset(candidate.lineno, candidate.col_offset)
        elif hasattr(candidate, '_fields'):  # pragma: no cover (PY35+)
            for field in reversed(candidate._fields):
                candidates.append(getattr(candidate, field))
    else:
        raise AssertionError(node)


class FindNodes(ast.NodeVisitor):
    def __init__(self):
        # multiple calls can report their starting position as the same
        self.calls = collections.defaultdict(list)
        self.funcs = {}
        self.literals = {}
        self.tuples = {}
        self.imports = set()
        self.classes = {}

    def visit_Tuple(self, node):
        if node.elts:
            # in < py38 tuples lie about offset -- later we must backtrack
            if sys.version_info < (3, 8):  # pragma: no cover (<py38)
                self.tuples[_to_offset(node)] = Literal(node)
            else:  # pragma: no cover (py38+)
                self.literals[_to_offset(node)] = Literal(node)
        self.generic_visit(node)


def _find_tuple(i, tokens):  # pragma: no cover (<py38)
    # tuples are evil, we need to backtrack to find the opening paren
    i -= 1
    while tokens[i].name in NON_CODING_TOKENS:
        i -= 1
    # Sometimes tuples don't even have a paren!
    # x = 1, 2, 3
    if tokens[i].src != '(':
        return False
    return True


def _changing_list(lst):
    i = 0
    while i < len(lst):
        yield i, lst[i]
        i += 1


def _find_danger(contents_text):
    try:
        ast_obj = ast_parse(contents_text)
    except SyntaxError:
        return contents_text
    dangers = []
    visitor = FindNodes()
    visitor.visit(ast_obj)
    tokens = src_to_tokens(contents_text)
    for i, token in _changing_list(tokens):
        if not token.src:
            continue
        if token.offset in visitor.tuples:
            t: ast.Tuple = visitor.tuples[token.offset][0]
            if len(t.elts) == 1:
                r = _find_tuple(i, tokens)
                if not r:
                    line = token.offset.line
                    dangers.append(
                        (line, contents_text.splitlines()[line - 1]))
    return dangers


def find_in_file(filename):
    with open(filename, 'rb') as f:
        contents_bytes = f.read()

    try:
        contents_text = contents_bytes.decode('UTF-8')
    except UnicodeDecodeError:
        print('{} is non-utf-8 (not supported)'.format(filename))
        return 1

    dangers = _find_danger(contents_text)

    if dangers:
        for line_no, danger_line_content in dangers:
            print(
                '{}:{} has single element tuple with no brackets "{}"'.format(
                    filename, line_no, danger_line_content))
        return 1

    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args(argv)

    ret = 0
    for filename in args.filenames:
        ret |= find_in_file(filename)
    return ret


if __name__ == '__main__':
    exit(main())
