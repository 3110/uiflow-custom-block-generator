import re

DEFAULT_ENCODING = "utf-8"
DEFAULT_PYTHON_CODE_INDENT = 4
DEFAULT_JSON_INDENT = 2

KEY_ARGS = "args"
KEY_BLOCKS = "blocks"
KEY_CATEGORY = "category"
KEY_CODE = "code"
KEY_COLOR = "color"
KEY_JSCODE = "jscode"
KEY_NAME = "name"
KEY_TEXT = "text"
KEY_TYPE = "type"
KEY_PARAMS = "params"

FIELD_LABEL = "field_label"
FIELD_INPUT = "field_input"
FIELD_NUMBER = "field_number"
INPUT_VALUE = "input_value"

VALUE = "value"

BLOCK_PARAM_TYPE_LABEL = "label"
BLOCK_PARAM_TYPE_STRING = "string"
BLOCK_PARAM_TYPE_NUMBER = "number"
BLOCK_PARAM_TYPE_VARIABLE = "variable"

BLOCK_PARAM_TYPES = [
    BLOCK_PARAM_TYPE_LABEL,
    BLOCK_PARAM_TYPE_STRING,
    BLOCK_PARAM_TYPE_NUMBER,
    BLOCK_PARAM_TYPE_VARIABLE,
]

BLOCK_TYPE_VALUE = VALUE
BLOCK_TYPE_EXECUTE = "execute"

M5B_REQUIRED_KEYS = [KEY_CATEGORY, KEY_COLOR, KEY_BLOCKS, KEY_JSCODE]

BLOCK_NAME_FORMAT = "__{category}_{name}"
BLOCK_NAME_PARSER = re.compile(r"__([^_]+)_([^_]+)")

EXT_M5B = "m5b"
EXT_PY = "py"
EXT_JSON = "json"


def to_camel(s):
    w = re.split(r"[\s_-]", s.lower())
    return "".join([v if p == 0 else v.capitalize() for p, v in enumerate(w)])


def to_snake(s):
    return '_'.join(
        re.sub(
            '([A-Z0-9]+[a-z]+)', r' \1', re.sub('([A-Z0-9]+)', r' \1', s.replace('-', ' ').replace('_', ' '))
        ).split()
    ).lower()
