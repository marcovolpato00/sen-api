import math
from functools import wraps
from json import dumps as json_dumps

import click
from click import echo, clear
from halo import Halo
from rich.console import Console
from rich.table import Table
from loguru import logger

from sen_api import SENProvider, Config, __version__, AuthenticationError


__all__ = [
    'cli'
]


config = Config()
provider = SENProvider(config=config)

console = Console()


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # if not already authenticated, try to authenticate
        if not provider.is_authenticated:
            try:
                provider.authenticate()
            except (AuthenticationError, ValueError):
                echo('Cannot authenticate.')
                return None
        return f(*args, **kwargs)
    return wrapper

########################################################################################################################


@click.group()
@click.version_option(__version__)
@click.option('--verbose', '-v', help='Enable verbose logs.', is_flag=True)
@click.option('--json', '-j', help='Print in JSON format when possible.', is_flag=True)
@click.pass_context
def cli(ctx, verbose, json):
    ctx.ensure_object(dict)
    if not verbose:
        logger.remove()
    ctx.obj['JSON'] = json
    config.load()

########################################################################################################################


def _authenticate(username=None, password=None, force=False):
    clear()

    success = True
    with Halo(text='Authenticating', spinner='dots'):
        try:
            if force:
                provider.authenticate(force=True)
            else:
                provider.authenticate(username, password, force=True)
        except (AuthenticationError, ValueError):
            logger.error('Error while trying to authenticate.')
            success = False

    if success:
        if not force:
            config.write('auth', {
                'username': username,
                'password': password
            })
        echo('Successfully authenticated.')
    else:
        echo('Cannot authenticate, check your credentials.')


def force_authentication(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    _authenticate(force=True)
    ctx.exit()


@cli.command()
@click.option('--username', '-u', prompt=True)
@click.option('--password', '-p', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--force', '-f', help='Force authentication using saved credentials.', is_flag=True,
              callback=force_authentication, expose_value=False, is_eager=True)
def authenticate(username, password):
    _authenticate(username, password)

########################################################################################################################


@auth_required
def last_reading(json):
    reading = provider.get_last_reading()

    if json:
        echo(json_dumps(reading))
    else:
        band_readings = reading['readings']

        table = Table(title=reading['reading_date'])
        table.add_column('Time band')
        table.add_column('Consumption')

        table.add_row('A1', band_readings['A1'], style='red')
        table.add_row('A2', band_readings['A2'], style='yellow')
        table.add_row('A3', band_readings['A3'], style='green')

        console.print(table)


@auth_required
def all_readings(json):
    readings_list = provider.get_all_readings()

    if json:
        echo(json_dumps([r.to_dict() for r in readings_list]))
    else:
        avg_consumption_avg = 0
        if len(readings_list) != 0:
            avg_consumption_avg = math.ceil(sum(r.avg_consumption for r in readings_list) / len(readings_list))

        table = Table(title='Readings')
        table.add_column('Start', style='cyan')
        table.add_column('End', style='green')
        table.add_column('Days')
        table.add_column('Total consumption', justify='center')
        table.add_column('Mean consumption', justify='center')
        for r in readings_list:
            color = 'red' if r.avg_consumption > avg_consumption_avg else 'default'
            table.add_row(
                str(r.interval_start.date()),
                str(r.interval_end.date()),
                str(r.interval_days),
                str(r.total_consumption),
                f'[{color}]{str(r.avg_consumption)}[/{color}]'
            )

        console.print(table)
        console.print('Values above the mean are colored [red]red[/red].\n')


@cli.command()
@click.option('--all', '-a', '_all', help='Get all readings.', is_flag=True)
@click.option('--last', '-l', help='Get only the last readings.', is_flag=True)
@click.pass_context
def readings(ctx, _all, last):
    json = ctx.obj['JSON']
    if _all:
        all_readings(json)
    elif last:
        last_reading(json)
    else:
        echo(ctx.get_help())
        ctx.exit()

########################################################################################################################


@cli.command()
@click.pass_context
@auth_required
def client_info(ctx):
    values = provider.client_info

    if ctx.obj['JSON']:
        echo(json_dumps(values))
    else:
        table = Table(title='Client info')
        table.add_column('Field')
        table.add_column('Value')
        for v in values.keys():
            table.add_row(v, values[v])

        console.print(table)

########################################################################################################################


@cli.command()
@click.option('--year', '-y', help='Specify the bills year.')
@click.option('--download', '-d', type=int, help='Download bill with the specified in PDF format.')
@click.pass_context
@auth_required
def bills(ctx, year, download):
    json = ctx.obj['JSON']
    if not year:
        years = provider.get_bills_available_years()
        if json:
            echo(json_dumps({'available_years': years}))
        else:
            table = Table(title='Available years')
            table.add_column('Year', width=15, justify='center')
            for year in years:
                table.add_row(year)

            console.print(table)
    else:
        try:
            bills_list = provider.get_bills(year=year)
        except ValueError as e:
            echo(e)
            ctx.exit()

        if download:
            found_bill = None
            for bill in bills_list:
                if bill.number == download:
                    found_bill = bill

            if not found_bill:
                echo(f'Bill with number {download} not found.')
                ctx.exit()

            with Halo(text=f'Downloading {found_bill.document_name} ...', spinner='dots'):
                download_path = provider.download_bill(found_bill)

            if download_path:
                console.print(f'Bill successfuly downloaded in [cyan]{download_path}[/cyan]')
            else:
                echo('Error during the download, enable verbose output for more details.')

        else:
            if json:
                echo(json_dumps([b.to_dict() for b in bills_list]))
            else:
                avg_amount = 0
                if len(bills_list) != 0:
                    avg_amount = math.ceil(sum(b.amount for b in bills_list) / len(bills_list))

                table = Table(title=f'Year [cyan]{year}[/cyan] bills')
                table.add_column('Number')
                table.add_column('Due date')
                table.add_column('Amount')
                table.add_column('Payed')
                for b in bills_list:
                    amount_color = 'red' if b.amount > avg_amount else 'default'
                    table.add_row(
                        str(b.number),
                        str(b.due_date.date()),
                        f'[{amount_color}]{str(b.amount)}€[/{amount_color}]',
                        '[green]Yes[/green]' if b.is_payed else '[red]No[/red]'
                    )

                console.print(table)
                console.print('Values above the mean are colored [red]red[/red].\n')
