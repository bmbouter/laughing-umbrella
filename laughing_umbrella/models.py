from django.db import models


class Repository(models.Model):

    url = models.URLField(unique=True, blank=False)

    @property
    def issues_url(self):
        if self.url.endswith('/'):
            issue_portion = 'issues?state=all'
        else:
            issue_portion = '/issues?state=all'
        return self.url + issue_portion


class Issue(models.Model):

    BUG = 'B'
    FEATURE = 'F'
    OTHER = 'O'
    SECURITY = 'S'

    CODING_CHOICES = (
        (BUG, 'Bug'),
        (FEATURE, 'Feature'),
        (OTHER, 'Other'),
        (SECURITY, 'Security'),
    )

    url = models.URLField(unique=True, blank=False)
    text = models.TextField()
    type = models.CharField(max_length=1, choices=CODING_CHOICES)
    repository = models.ForeignKey('Repository', on_delete=models.CASCADE, blank=False,
                                   related_name='issues')

    labels_url = models.URLField(unique=True, blank=False)
    comments_url = models.URLField(unique=True, blank=False)
    html_url = models.URLField(unique=True, blank=False)


class Comment(models.Model):

    url = models.URLField(unique=True, blank=False)
    text = models.TextField()
    issue = models.ForeignKey('Issue', on_delete=models.CASCADE, blank=False,
                              related_name='comments')


class PullRequest(models.Model):

    url = models.URLField(unique=True, blank=False)
    html_url = models.URLField(unique=True, blank=False)
    text = models.TextField()
    issue = models.ForeignKey('Issue', on_delete=models.CASCADE, blank=False,
                              related_name='pull_requests')
