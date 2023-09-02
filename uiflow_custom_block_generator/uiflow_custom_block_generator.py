import json
import os

from .uiflow_custom_block import *

KEY_COLOUR = "colour"  # for m5b
KEY_MESSAGE = "message"
KEY_OUTPUT = "output"
KEY_PREVIOUS_STATEMENT = "previousStatement"
KEY_NEXT_STATEMENT = "nextStatement"
KEY_SPELL_CHECK = "spellcheck"
KEY_VALUE = VALUE

BLOCK_SETTING_REQUIRED_KEYS = [KEY_CATEGORY, KEY_COLOR, KEY_BLOCKS]
BLOCK_REQUIRED_KEYS = [KEY_NAME, KEY_TYPE]
BLOCK_PARAM_REQUIRED_KEYS = [KEY_NAME, KEY_TYPE]

BLOCK_TYPE_PARAMS = {
    BLOCK_TYPE_VALUE: {
        KEY_OUTPUT: None,
    },
    BLOCK_TYPE_EXECUTE: {
        KEY_PREVIOUS_STATEMENT: None,
        KEY_NEXT_STATEMENT: None,
    },
}

TEMPLATE_FILENAME = "{root}.{ext}"

TEMPLATE_BLOCK_COMMENT = "// Block {block_name}"

TEMPLATE_BLOCK_CODE_VARIABLE = (
    "var {var_name} = Blockly.Python.valueToCode(block, '{var_name}', Blockly.Python.ORDER_NONE);"
)
TEMPLATE_BLOCK_CODE_FIELD_VALUE = "var {var_name} = block.getFieldValue('{var_name}');"

TEMPLATE_BLOCK_JSON_CODE = "var {block_name}_json = {json};"

TEMPLATE_BLOCK_DEFINITION = '''window['Blockly'].Blocks['{block_name}'] = {{
    init: function() {{
        this.jsonInit({block_name}_json);
    }}
}};
'''

TEMPLATE_BLOCK_CODE = {
    BLOCK_TYPE_VALUE: '''window['Blockly'].Python['{block_name}'] = function(block) {{
    {vars}return [`{python_code}`, Blockly.Python.ORDER_CONDITIONAL]
}};
''',
    BLOCK_TYPE_EXECUTE: '''window['Blockly'].Python['{block_name}'] = function(block) {{
    {vars}return `{python_code}\n`
}};
''',
}


class UIFlowCustomBlockGeneratorError(Exception):
    pass


class LabelParameterGenerator:
    def generate_args(self, pos, name):
        return {f"{KEY_MESSAGE}{pos}": "%1", f"{KEY_ARGS}{pos}": [{KEY_TYPE: FIELD_LABEL, KEY_TEXT: str(name)}]}

    def generate_vars(self, name):
        return ""


class StringParameterGenerator:
    def generate_args(self, pos, name):
        return {
            f"{KEY_MESSAGE}{pos}": "%1 %2",
            f"{KEY_ARGS}{pos}": [
                {KEY_TYPE: FIELD_LABEL, KEY_TEXT: str(name)},
                {KEY_TYPE: FIELD_INPUT, KEY_TEXT: "", KEY_SPELL_CHECK: False, KEY_NAME: str(name)},
            ],
        }

    def generate_vars(self, name):
        return TEMPLATE_BLOCK_CODE_FIELD_VALUE.format(var_name=name)


class NumberParameterGenerator:
    def generate_args(self, pos, name):
        return {
            f"{KEY_MESSAGE}{pos}": "%1 %2",
            f"{KEY_ARGS}{pos}": [
                {KEY_TYPE: FIELD_LABEL, KEY_TEXT: str(name)},
                {KEY_TYPE: FIELD_NUMBER, KEY_VALUE: 0, KEY_NAME: str(name)},
            ],
        }

    def generate_vars(self, name):
        return TEMPLATE_BLOCK_CODE_FIELD_VALUE.format(var_name=name)


class VariableParameterGenerator:
    def generate_args(self, pos, name):
        return {
            f"{KEY_MESSAGE}{pos}": "%1 %2",
            f"{KEY_ARGS}{pos}": [
                {KEY_TYPE: FIELD_LABEL, KEY_TEXT: str(name)},
                {KEY_TYPE: INPUT_VALUE, KEY_NAME: name},
            ],
        }

    def generate_vars(self, name):
        return TEMPLATE_BLOCK_CODE_VARIABLE.format(var_name=name)


class ParameterGenerator:
    def __init__(self):
        self.generators = {
            BLOCK_PARAM_TYPE_LABEL: LabelParameterGenerator(),
            BLOCK_PARAM_TYPE_STRING: StringParameterGenerator(),
            BLOCK_PARAM_TYPE_NUMBER: NumberParameterGenerator(),
            BLOCK_PARAM_TYPE_VARIABLE: VariableParameterGenerator(),
        }

    def generate_args(self, params):
        args = {}
        for pos, p in enumerate(params):
            args.update(self.generators[p[KEY_TYPE]].generate_args(pos, p[KEY_NAME]))
        return args

    def generate_vars(self, params):
        return [self.generators[p[KEY_TYPE]].generate_vars(p[KEY_NAME]) for p in params]


class BlockGenerator:
    def __init__(self, base_dir, logger=None):
        self.logger = logger
        self.base_dir = base_dir
        self.param_generator = ParameterGenerator()

    def validate_parameter_types(self, block_name, params):
        for pos, p in enumerate(params):
            if not p[KEY_TYPE] in BLOCK_PARAM_TYPES:
                raise UIFlowCustomBlockGeneratorError(
                    "Illegal Parameter Type: {type} (#{pos} parameter in the block \"{name}\")".format(
                        type=p[KEY_TYPE], pos=pos + 1, name=block_name
                    )
                )

    def validate(self, block):
        validate_argument(block, dict)
        validate_required_keys(block, BLOCK_REQUIRED_KEYS, "block")
        self.validate_parameter_types(block[KEY_NAME], block.get(KEY_PARAMS, []))

    def load(self, name, encoding=DEFAULT_ENCODING):
        file_path = os.path.normpath(os.path.join(self.base_dir, TEMPLATE_FILENAME.format(root=name, ext=EXT_PY)))
        self.logger.debug(f"Block Code: {file_path}")
        with open(file_path, "r", encoding=encoding) as f:
            return "\n".join([line.rstrip() for line in f.readlines()])

    def generate(self, category, color, block):
        self.validate(block)
        name = block[KEY_NAME]
        block_name = BLOCK_NAME_FORMAT.format(category=category, name=to_camel(name))

        params = block[KEY_PARAMS]
        args = {}
        args.update(BLOCK_TYPE_PARAMS[block[KEY_TYPE]])
        args.update(self.param_generator.generate_args(params))
        args.update({KEY_COLOUR: color})

        vs = self.param_generator.generate_vars(params)
        result = [
            TEMPLATE_BLOCK_COMMENT.format(block_name=block_name),
            TEMPLATE_BLOCK_JSON_CODE.format(
                block_name=block_name, json=json.dumps(args, ensure_ascii=False, indent=DEFAULT_PYTHON_CODE_INDENT)
            ),
            TEMPLATE_BLOCK_DEFINITION.format(block_name=block_name),
            TEMPLATE_BLOCK_CODE[block[KEY_TYPE]].format(
                block_name=block_name, vars="".join([v + "\n" for v in vs]), python_code=self.load(name)
            ),
        ]
        return result


class UIFlowCustomBlockGenerator:
    def __init__(self, config_file, target_dir=None, logger=None):
        self.logger = logger
        with open(config_file, 'r', encoding="UTF-8") as config:
            self.config = json.load(config)
            validate_required_keys(self.config, BLOCK_SETTING_REQUIRED_KEYS, "setting")
        self.base_dir = os.path.abspath(os.path.dirname(config.name))
        self.target_dir = os.path.abspath(target_dir) if target_dir else self.base_dir
        self.filename = os.path.splitext(os.path.basename(config.name))[0]
        self.block_generator = BlockGenerator(self.base_dir, logger)

    def generate(self):
        category = self.config[KEY_CATEGORY]
        color = self.config[KEY_COLOR]
        m5b = {KEY_CATEGORY: category, KEY_COLOR: color, KEY_BLOCKS: [], KEY_JSCODE: ""}
        for block in self.config[KEY_BLOCKS]:
            m5b[KEY_BLOCKS].append(BLOCK_NAME_FORMAT.format(category=category, name=to_camel(block[KEY_NAME])))
            m5b[KEY_JSCODE] += "\n".join(self.block_generator.generate(category, color, block))
        self.dump(m5b)

    def dump(self, data, encoding=DEFAULT_ENCODING):
        file_path = os.path.normpath(
            os.path.join(self.target_dir, TEMPLATE_FILENAME.format(root=self.filename, ext=EXT_M5B))
        )
        self.logger.debug("Write M5B: " + file_path)
        with open(file_path, "w", encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False)
