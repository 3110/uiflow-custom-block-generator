[English](README.md)

# UiFlow 用のカスタムブロックファイルを生成する

カスタムブロック設定 JSON ファイルと [MicroPython](https://micropython.org/) ファイルから [UiFlow](https://flow.m5stack.com/) 用のカスタムブロックファイル（M5B ファイル）を生成します。

## インストール

私は 64 ビット版の Windows 11 上で VS Code，Git Bash，Python v3.10.4 を使って開発・動作確認をしています。

以下のコマンドを実行してインストールします。

```bash
pip install https://github.com/3110/uiflow-custom-block-geneartor
```

## カスタムブロックの設定方法

カスタムブロックの設定用 JSON は以下のような構造になっています。

```json
{
  "category": "ATOM_Babies",
  "color": "#115f07",
  "blocks": [
    {
      "name": "init_atom_babies",
      "type": "execute",
      "params": [
        { "name": "ATOM Babiesを初期化する", "type": "label" },
        { "name": "_eye_color", "type": "variable" },
        { "name": "_cheek_color", "type": "variable" },
        { "name": "_background_color", "type": "variable" }
      ]
    },
    {
      "name": "rgb",
      "type": "value",
      "params": [
        { "name": "色を指定する", "type": "label" },
        { "name": "_r", "type": "number" },
        { "name": "_g", "type": "number" },
        { "name": "_b", "type": "number" }
      ]
    }
  ]
}
```

- `category`: UiFlow Block Maker の Namespace に対応します。
- `color`: ブロックの色を`#RRGGBB`で指定します。
- `blocks`: カスタムブロックを定義します。ここに現れる順番でブロックが並びます。

`blocks`で指定するカスタムブロックは以下のよう定義します。

- `name`: ブロックのコードを読み込むためのファイル名。例えば`"name": "rgb"`の場合，設定用 JSON と同じディレクトリにある`rgb.py`を読み込みます。
- `type`: ブロックの種類を指定します。値を返すブロック（`value`）と実行するブロック（`execute`）の 2 種類指定できます。
- `params`: ブロックに渡す引数を定義します。ここに現れる順番通りに定義されます。

`params`で指定する引数は以下のように定義します。

- `name`: 引数の名前。`type`が`label`の場合はブロックに表示される文字列
- `type`: 引数の型。以下の 4 種類が用意されています。
  - `label`: ブロックに表示するラベル。複数指定可能
  - `string`: 文字列
  - `number`: 数値
  - `variable`: 変数。他のブロックとも接続できます。

`examples/atom_babies`に設定のサンプルを用意してあるので参考にしてください。

## 実行方法

以下を実行すると，設定用 JSON と同じディレクトリに`atom_babies.m5b`を生成します。

```bash
python -m uiflow-custom-block-generator examples/atom_babies/atom_babies.json
```

`--target_dir`（`-t`）オプションで M5B ファイルの出力先ディレクトリを変更できます。以下の例の場合，カレントディレクトリに`atom_babies.m5b`を生成します。

```bash
python -m uiflow-custom-block-generator examples/atom_babies/atom_babies.json -t .
```

注意：このスクリプトで生成された M5B ファイルは UiFlow Block Editor で正常に読み込めません（長い Python コードが途中で切られてしまう問題があります）。

## VSCode での注意点

- ブロックの引数を参照する`${}`が Flake8 で Invalid Syntax（E999）になるため，`.vscode/settings.json`で E999 を抑制しています。
- MicroPython の`rgb`モジュールを使うコードには`# type: ignore # noqa: F821`（undefined name を無視する）を付けてください（Pylance と Flake8 の警告抑制）。
