import asyncio

from laughing_umbrella.fetch import ingest_repo


from django.core.management.base import BaseCommand


def main(url, limit):
    # import pydevd
    # pydevd.settrace('localhost', port=17264, stdoutToServer=True, stderrToServer=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ingest_repo(url, limit))


class Command(BaseCommand):
    help = 'Ingest/Update github issues for a project.'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='The api url of the repo to sync. e.g. '
            'https://api.github.com/repos/geerlingguy/ansible-role-firewall/')
        parser.add_argument('--limit', type=int, help='Limit the number of imported issues, e.g. '
                                                      '10.')

    def handle(self, *args, **options):
        url = options['url']
        limit = options['limit']
        main(url, limit)
