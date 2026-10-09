"""CLI writes only to stdout; shell redirection is controlled by the operator."""
import argparse
import json
import sys
from . import __version__
from .engine import audit, markdown
from .schema import InputError, load


def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline read-only Azure/Entra normalized snapshot auditor (no cloud connection).')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('snapshot', help='Path to a normalized v1 JSON snapshot; never a raw tenant export')
    parser.add_argument('--format', choices=('json', 'markdown'), default='json')
    parser.add_argument('--as-of', help='UTC YYYY-MM-DDTHH:MM:SSZ for reproducible historical replay')
    parser.add_argument('--max-age-days', type=int, default=7)
    args = parser.parse_args(argv)
    try:
        report = audit(load(args.snapshot), as_of=args.as_of, max_age_days=args.max_age_days)
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + '\n' if args.format == 'json' else markdown(report))
        return report['exit_code']
    except InputError as exc:
        sys.stderr.write(f'Input error: {exc}\n')
        return 2
    except BrokenPipeError:
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
