#! 

import sys
from datetime import date

import click
import os
import yaml

from os.path import exists
from pathlib import Path

from api.notion import get_journal_database, get_current_months_journal, append_entry

CONFIG_DIR = os.getenv('BLOG_CLI_CONF_DIR') or f"{str(Path.home())}/.config/blog-cli"


def get_configuration():
    def ensure_configuration():
        if not exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

        if not exists(f'{CONFIG_DIR}/configrc'):
            open(f'{CONFIG_DIR}/configrc', 'w')

    ensure_configuration()
    with open(f'{CONFIG_DIR}/configrc', 'r') as configFile:
        return yaml.safe_load(configFile) or {}


def write_configuration(configuration):
    if not configuration:
        return

    with open(f'{CONFIG_DIR}/configrc', 'w') as configFile:
        yaml.safe_dump(configuration, configFile)

    return


@click.group(invoke_without_command=True)
def blog():
    configuration = get_configuration()
    if not configuration:
        click.echo("Please configure this tool before attempting to blog!")
        return

    current_month_page = get_current_months_journal(configuration['JOURNAL_DBID'], configuration['API_KEY'])
    if not current_month_page:
        click.echo('Unable to find or create a journal page for the current month. Please check your configurations')

    is_snippet = input('Do you want to jot down a quick note (Y/n): ') == 'Y'
    if is_snippet:
        lines = [str(date.today())]
        click.echo("What did you do today?")
        while True:
            line = sys.stdin.readline().rstrip('\n')
            if line == '':
                break
            lines.append(line)

        entry = "\n".join(lines)

        success = append_entry(entry, configuration['API_KEY'], current_month_page)
        click.echo(f"Success: {success}")

    else:
        click.echo("Full blog entries are not yet supported")


@blog.command()
def configure():
    configuration = get_configuration()

    if 'API_KEY' not in configuration:
        configuration['API_KEY'] = input('What is your Notion API Key: ').strip()
        click.echo('')

    if 'JOURNAL_DBID' not in configuration:
        has_dbid = input('Do you know the database ID of your Journal in Notion (Y/n): ') == 'Y'
        if has_dbid:
            configuration['JOURNAL_DBID'] = input('Please enter your notion database ID (a UUID with or without dashes): ')
        else:
            journal_title = input('What is the title of your Journal in Notion: ')
            potential_journals = get_journal_database(journal_title, configuration['API_KEY'])
            for journal in potential_journals:
                click.echo(f'{journal["index"]}: {journal["name"]}')

            journal_index = int(input("Please select your Journal by the number displayed: "))
            configuration['JOURNAL_DBID'] = potential_journals[journal_index]['id']

    write_configuration(configuration)


if __name__ == '__main__':
    blog()
