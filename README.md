# SUTD Temperature Taking System Command Line Interface

## Usage

```
usage: tts_cli.py [-h] [-t] [-d] username password

SUTD Temperature Taking System Command Line Interface

positional arguments:
  username              SUTD Student ID
  password              SUTD Password

optional arguments:
  -h, --help                show this help message and exit
  -t, --temperature         submit temperature taking result
  -d, --daily-declaration   submit daily declaration
```

## Example

``` bash
python tts_cli.py -t -d 1001234 Sutd1234
```