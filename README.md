[日本語版](README_ja_JP.md)

# Generating a custom block file for [UiFlow](https://flow.m5stack.com)

This script generates a custom block file(the M5B file) from a JSON file for setting custom blocks, and [MicroPython](https://micropython.org/) files defined codes for custom blocks.

You can also generate the JSON and MicroPython files from an existing M5B file.

## Installation

I have developed and tested this script using VS Code, Git Bash, and Python v3.10.4 on the Windows 11 environment.

To install this script, execute the following:

```bash
pip install git+https://github.com/3110/uiflow-custom-block-generator
```

## Setting Custom Blocks

The structure of the JSON file for setting custom blocks is the following:

```json
{
  "category": "ATOM_Babies",
  "color": "#115f07",
  "blocks": [
    {
      "name": "init_atom_babies",
      "type": "execute",
      "params": [
        { "name": "Initialize ATOM Babies", "type": "label" },
        { "name": "_eye_color", "type": "variable" },
        { "name": "_cheek_color", "type": "variable" },
        { "name": "_background_color", "type": "variable" }
      ]
    },
    {
      "name": "rgb",
      "type": "value",
      "params": [
        { "name": "Specify the color", "type": "label" },
        { "name": "_r", "type": "number" },
        { "name": "_g", "type": "number" },
        { "name": "_b", "type": "number" }
      ]
    }
  ]
}
```

- `category`: Same as Namespace on the [UiFlow Block Maker](http://block-maker.m5stack.com/).
- `color`: Specify the color of custom blocks with `#RRGGBB`.
- `blocks`: Define custom blocks. They are arranged in the order in which they appear here.

To define custom blocks, specify the following items in `blocks`:

- `name`: Filename of MicroPython codes for the custom block. The setting `"name": "rgb"` means `rgb.py` is read from the same directory as the JSON file.
- `type`: Type of the custom block. You can specify the two types of blocks: `value`(the block returns a value) and `execute`(the block does not return any value).
- `params`: Arguments for the custom block. They are arranged in the order in witch they appear here.

To define arguments of the custom block, specify the following items in `params`.

- `name`: The name of the argument. If `type` is `label`, this is the label shown on the block.
- `type`: The type of the argument. There are four types:
  - `label`: The label displayed on the block. Multiple specifications are allowed.
  - `string`: String.
  - `number`: Number.
  - `variable`: Variable.

Please refer to `examples/atom_babies` for the sample.

## Execution

### Generating the M5B file from the JSON file and MicroPython files

To generate `atom_babies.m5b` on the same directory as the JSON file, execute the following:

```bash
python -m uiflow_custom_block_generator examples/atom_babies/atom_babies.json
```

You can specify `--target_dir`(`-t`) option to change the output directory of the M5B file.

For example, `atom_babies.m5b` is generated on the current directory if you execute the following:

```bash
python -m uiflow_custom_block_generator examples/atom_babies/atom_babies.json -t .
```

**Caution**: [UiFlow Block Maker](http://block-maker.m5stack.com/) cannot read the M5B file generated from this script.

### Generating the JSON file and MicroPython files from the M5B file

The following command creates the `atom_babies` directory in the same directory as the M5B file and generates `atom_babies.json` and the MicroPython files in the `atom_babies` directory.

```bash
python -m uiflow_custom_block_generator example/atom_babies/atom_babies.m5b
```

You can specify `--target_dir`(`-t`) option to change the output directory of the JSON file and MicroPython files. The following command creates `atom_babies` directory in the current directory.

```bash
python -m uiflow_custom_block_generator examples/atom_babies/atom_babies.m5b -t .
```

## Notes on VS Code

- Because Flake8 detects Invalid Syntax(E999) for `${}`(the reference to the argument of the custom block), the setting in `.vscode/settings.json` suppresses E999.
- If you use `rgb` modules in the custom block codes, you have to specify `# type: ignore # noqa: F821` to ignore undefined name errors.
