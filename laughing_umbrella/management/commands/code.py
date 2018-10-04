from django.core.management.base import BaseCommand

from laughing_umbrella.models import Issue


def main():
    for issue in Issue.objects.filter(type=''):
        msg = '\n\nIssue: {url}\n\nIs it a Bug/Feature/Security/Other [B/F/O/S]?'
        html_url = issue.url.replace('api.github.com/repos', 'github.com')
        issue.type = input(msg.format(url=html_url))
        issue.save()


class Command(BaseCommand):
    help = 'Interactively asks the user to code uncoded issues.'

    def handle(self, *args, **options):
        main()
