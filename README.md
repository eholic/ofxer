[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
# Ofxer
CSV to OFX converter.
A script of converting CSV files exporting from your credit and bank account

> mostly using csv2ofx function

## Requirements
```sh
$ pip install csv2ofx pandas
```

## Usage
### terminal
```sh
$ python ofxer.py -s 1 -c 0 1 2 your_credit.csv
$ python ofxer.py -s 1 -c 0 1 2 4 your_bank.csv
```

```
$ python ofxer.py --help
usage: ofxer.py [-h] [-p PARSER] [-o OUTPUT] -s SKIPROWS [-e ENCODING] -c
                USECOLS [USECOLS ...]
                csvfile

CSV to OFX converter.
A script of converting CSV files exporting from your credit and bank account

positional arguments:
  csvfile               csv file exported from your credit or bank acount

optional arguments:
  -h, --help            show this help message and exit
  -p PARSER, --parser PARSER
                        specify the date format if special e.g. '%Y年%m月%d日'
  -o OUTPUT, --output OUTPUT
                        path to write ofx file (default: output.ofx)
  -s SKIPROWS, --skiprows SKIPROWS
                        skipping number of csv file headers (incl. column name)
  -e ENCODING, --encoding ENCODING
                        file encoding
  -c USECOLS [USECOLS ...], --usecols USECOLS [USECOLS ...]
                        column index number of
                          date title amount
                          (e.g. --usecols 0 4 5)
                          or
                          date title withdraw deposit
                          (e.g. --usecols 0 3 10 5)
                          Note: counting from ZERO
```

### your python script
```python
from ofxer import Ofxer
options = {
    'credit1': {'skiprows': 10, 'usecols': [0, 1, 8]   },
    'credit2': {'skiprows':  7, 'usecols': [0, 1, 2]   },
    'bank':    {'skiprows':  1, 'usecols': [0, 1, 4, 3]},
    }
credit1 = Ofxer('data/credit1.csv', options['credit1'])
print(credit1._df)
credit1.write_ofx('credit1.ofx')
```

### License
This code is released under the MIT License, see ![LICENSE](LICENSE)


# Ofxer (In Japanese)

クレジットカードや銀行のcsvをOFXフォーマットに変換するスクリプト

## 使い方
### ターミナル
```sh
$ python ofxer.py -s 1 -c 0 1 2 -e cp932 your_credit.csv
$ python ofxer.py -s 1 -c 0 1 2 4 -e cp932 your_bank.csv
```

```
-s csvファイルの先頭を飛ばす行数(ヘッダーを含む)
-c 日付 タイトル 支払額
　　または
   日付 タイトル 出金額 入金額
   の列番号　※カウントは0から
-e 文字コードの指定
```

### Python
```python
from ofxer import Ofxer

options = {
    'orico':   {'skiprows': 10, 'usecols': [0, 1, 8],    'encoding': 'cp932'},
    'view':    {'skiprows':  7, 'usecols': [0, 1, 2],    'encoding': 'cp932'},
    'vpass':   {'skiprows':  1, 'usecols': [0, 1, 2],    'encoding': 'cp932'},
    'sony':    {'skiprows':  1, 'usecols': [0, 1, 4, 3], 'encoding': 'cp932'},
    'shinsei': {'skiprows':  1, 'usecols': [0, 1, 2, 3], 'encoding': 'cp932'},
    }
sony = Ofxer('data/YenFutsuRireki.csv', options['sony'])
sony.write_ofx('sony.ofx')
shinsei = Ofxer('data/JPY_CH_.csv', options['shinsei'])
print(shinsei._df)
shinsei.write_ofx('shinsei.ofx')
```

