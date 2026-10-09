"""CLI выводит только stdout/stderr; перенаправлением управляет оператор."""
import argparse
import json
import sys
from . import __version__
from .engine import audit, markdown
from .schema import InputError, load


class RussianParser(argparse.ArgumentParser):
    def format_usage(self):
        return super().format_usage().replace('usage:', 'Использование:', 1)

    def format_help(self):
        return super().format_help().replace('usage:', 'Использование:', 1)

    def error(self, message):
        replacements = {'unrecognized arguments:': 'неизвестные параметры:',
                        'the following arguments are required:': 'обязательные параметры:',
                        'invalid choice:': 'недопустимое значение:',
                        'choose from': 'выберите из', 'argument ': 'параметр ',
                        'expected one argument': 'ожидается одно значение',
                        'ignored explicit argument': 'явное значение недопустимо'}
        for old, new in replacements.items():
            message = message.replace(old, new)
        self.print_usage(sys.stderr)
        self.exit(2, f'Ошибка параметров: {message}\n')


def days(value):
    try:
        return int(value)
    except ValueError:
        raise argparse.ArgumentTypeError('ожидается целое число') from None


def main(argv=None):
    parser = RussianParser(add_help=False, description='Локальный аудитор Azure/Entra: только чтение нормализованного снимка, без подключения к облаку.')
    parser._positionals.title = 'Позиционные параметры'
    parser._optionals.title = 'Параметры'
    parser.add_argument('-h', '--help', action='help', help='показать справку и завершить работу')
    parser.add_argument('--version', action='version', version=__version__, help='показать версию пакета')
    parser.add_argument('snapshot', help='путь к нормализованному JSON-снимку v1; не сырой экспорт tenant')
    parser.add_argument('--format', choices=('json', 'markdown'), default='json', help='формат отчёта')
    parser.add_argument('--as-of', help='UTC YYYY-MM-DDTHH:MM:SSZ для воспроизводимой исторической оценки')
    parser.add_argument('--max-age-days', type=days, default=7, help='допустимый возраст снимка: 1–365 дней, по умолчанию 7')
    args = parser.parse_args(argv)
    try:
        report = audit(load(args.snapshot), as_of=args.as_of, max_age_days=args.max_age_days)
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + '\n' if args.format == 'json' else markdown(report))
        return report['exit_code']
    except InputError as exc:
        sys.stderr.write(f'Ошибка ввода: {exc}\n')
        return 2
    except BrokenPipeError:
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
