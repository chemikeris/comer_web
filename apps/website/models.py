from django.db import models
from django.contrib.sessions.models import Session

from apps.search.models import Job as SearchJob


class SessionJob(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    search_job = models.ForeignKey(SearchJob, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['session_id', 'search_job_id'],
                name='unique_session_job',
                ),
            ]


def set_and_get_session_jobs(request, search_job=None):
    "Get session jobs and set new session job"
    request.session['active'] = True
    request.session.save()
    session = Session.objects.get(pk=request.session.session_key)
    if search_job:
        SessionJob.objects.update_or_create(
            session=session,
            search_job=search_job
            )
    session_jobs = SessionJob.objects.select_related('search_job')\
        .filter(session=request.session.session_key)\
        .exclude(search_job__name='example')
    jobs = [sj.search_job for sj in session_jobs]
    return jobs

