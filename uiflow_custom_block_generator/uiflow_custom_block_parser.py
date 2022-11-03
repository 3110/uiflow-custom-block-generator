import json
import os

from .uiflow_custom_block import *

JSON_HEADER_FORMAT = 'var %s_json = {{' % BLOCK_NAME_FORMAT
CODE_HEADER_FORMAT = "window['Blockly'].Python['%s'] = function(block) {{" % BLOCK_NAME_FORMAT


class UiFlowCustomBlockParseError(Exception):
    pass


class ParameterParser:
    PARAM_TYPES = {
        FIELD_LABEL: BLOCK_PARAM_TYPE_LABEL,
        FIELD_INPUT: BLOCK_PARAM_TYPE_STRING,
        FIELD_NUMBER: BLOCK_PARAM_TYPE_NUMBER,
        INPUT_VALUE: BLOCK_PARAM_TYPE_VARIABLE,
    }

    def __init__(self, logger=None):
        self.logger = logger

    def parse(self, data):
        params = []
        args = [v for k, v in data.items() if k.startswith(KEY_ARGS)]
        for v in args:
            n_args = len(v)
            if n_args == 1:
                params.append({KEY_NAME: v[0][KEY_TEXT], KEY_TYPE: BLOCK_PARAM_TYPE_LABEL})
            elif n_args == 2:
                params.append({KEY_NAME: v[1][KEY_NAME], KEY_TYPE: self.PARAM_TYPES[v[1][KEY_TYPE]]})
        return params


class BlockParser:
    def __init__(self, logger=None):
        self.logger = logger
        self.param_parser = ParameterParser(self.logger)

    def extractRegion(self, header, footer, lines):
        inRegion = False
        region = []
        for line in lines:
            if inRegion:
                if line == footer:
                    inRegion = False
                    break
                region.append(line)
            else:
                if line.startswith(header):
                    inRegion = True
        if len(region) == 0:
            raise UiFlowCustomBlockParseError("No header found: %s", header)
        return region

    def extractCode(self, category, name, lines):
        header = CODE_HEADER_FORMAT.format(category=category, name=name)
        return self.extractRegion(header, '};', lines)

    def extractPythonCode(self, category, name, lines):
        codes = '\n'.join(self.extractCode(category, name, lines))
        start = codes.find('`') + 1
        end = codes.rfind('`')
        return codes[start:end].split('\n')

    def extractJSON(self, category, name, lines):
        header = JSON_HEADER_FORMAT.format(category=category, name=name)
        footer = '};'
        return json.loads('{' + ''.join(self.extractRegion(header, footer, lines)) + '}')

    def parseNames(self, blocks):
        return [name.split('_')[-1] for name in blocks]

    def parseType(self, category, name, codes):
        region = [r.strip() for r in self.extractCode(category, name, codes)]
        for r in region:
            if r.startswith('return `'):
                return BLOCK_TYPE_EXECUTE
            elif r.startswith('return ['):
                return BLOCK_TYPE_VALUE
        else:
            raise UiFlowCustomBlockParseError("Unknown Block Type: category = %s, name = %s" % (category, name))

    def parse(self, category, name, data):
        json_data = self.extractJSON(category, name, data)
        params = self.param_parser.parse(json_data)
        block_type = self.parseType(category, name, data)
        return {KEY_NAME: to_snake(name), KEY_TYPE: block_type, KEY_PARAMS: params}


class UiFlowCustomBlockParser:
    @classmethod
    def isCustomBlockFile(cls, filepath):
        return os.path.splitext(filepath)[1] == '.' + EXT_M5B

    def __init__(self, logger=None):
        self.logger = logger
        self.block_parser = BlockParser(self.logger)

    def parse(self, m5b_file, target_dir=None):
        m5b = None
        with open(m5b_file, mode='r', encoding="UTF-8") as f:
            m5b = json.load(f)
            self.logger.debug(json.dumps(m5b[KEY_JSCODE].split('\n'), indent=DEFAULT_JSON_INDENT))

        category = m5b[KEY_CATEGORY]

        if target_dir is None:
            target_dir = os.path.dirname(m5b_file)
        base_dir = os.path.join(os.path.abspath(target_dir), to_snake(category))

        js_codes = m5b[KEY_JSCODE].split('\n')
        setting, codes = {KEY_CATEGORY: category, KEY_COLOR: m5b[KEY_COLOR], KEY_BLOCKS: []}, {}
        for name in self.block_parser.parseNames(m5b[KEY_BLOCKS]):
            setting[KEY_BLOCKS].append(self.block_parser.parse(category, name, js_codes))
            codes[name] = self.block_parser.extractPythonCode(category, name, js_codes)
        return base_dir, setting, codes
