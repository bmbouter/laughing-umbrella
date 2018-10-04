from gettext import gettext as _
import json

import aiohttp

import django
django.setup()

from django.conf import settings
from laughing_umbrella.models import Comment, Issue, PullRequest, Repository


async def fetch_as_json(session, url):
    async with session.get(url) as response:
        response_text = await response.text()
        try:
            next_page_url = response.links['next']['url']
        except KeyError:
            pass
        else:
            raise Exception('Unhandled pages exist.')
        return json.loads(response_text)


async def fetch_and_save_comments(issue, url, session):
    async with session.get(url) as response:
        response_text = await response.text()
        try:
            next_page_url = response.links['next']['url']
        except KeyError:
            pass
        else:
            await fetch_and_save_comments(issue, next_page_url, session)
        comments_dict = json.loads(response_text)
    for comment_dict in comments_dict:
        comment, created = Comment.objects.get_or_create(issue=issue, url=comment_dict['url'])
        if created:
            comment.text = json.dumps(comment_dict)
            comment.save()


async def fetch_and_save_pull_request(issue, session):
    issue_dict = json.loads(issue.text)
    try:
        url = issue_dict['pull_request']['url']
    except KeyError:
        return
    pr_dict = await fetch_as_json(session, url)
    pull_request, created = PullRequest.objects.get_or_create(issue=issue, url=pr_dict['url'],
                                                              html_url=pr_dict['html_url'])
    if created:
        pull_request.text = json.dumps(pr_dict)
        pull_request.save()


async def fetch_and_save_issues(repo, url, limit, session, fetched_issues=0):
    async with session.get(url) as response:
        response_text = await response.text()
        try:
            next_page_url = response.links['next']['url']
        except KeyError:
            next_page_url = None
        issues_dict = json.loads(response_text)
        for issue_dict in issues_dict:
            if limit:
                if fetched_issues == limit:
                    return
            issue_data = {'repository': repo}
            for key in ['url', 'labels_url', 'comments_url', 'html_url']:
                issue_data[key] = issue_dict[key]
            issue_obj, created = Issue.objects.get_or_create(**issue_data)
            if created:
                issue_obj.text = json.dumps(issue_dict)
                issue_obj.save()
            await fetch_and_save_comments(issue_obj, issue_obj.comments_url, session)
            await fetch_and_save_pull_request(issue_obj, session)

            fetched_issues = fetched_issues + 1
        if next_page_url:
            # asyncio.get_event_loop().create_task(fetch_and_save_issues(repo, next_page_url, session))
            await fetch_and_save_issues(repo, next_page_url, limit, session, fetched_issues)
        if limit:
            if fetched_issues < limit:
                msg = _('--limit {limit} specified, but only {count} issues exist.')
                raise Exception(msg.format(limit=limit, count=fetched_issues))


async def ingest_repo(url, limit=None):
    headers = {"Authorization": "token {token}".format(token=settings.GITHUB_API_TOKEN)}
    repo, created = Repository.objects.get_or_create(url=url)
    async with aiohttp.ClientSession(headers=headers) as session:
        await fetch_and_save_issues(repo, repo.issues_url, limit, session)
