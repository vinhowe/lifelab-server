from typing import List, Dict

from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone

OPEN = "OPEN"
CLOSED = "CLOSED"
ISSUE_STATE_CHOICES = [(OPEN, "Open"), (CLOSED, "Closed")]

MAX_BODY_TEXT_LENGTH = 65536
MAX_TITLE_TEXT_LENGTH = 256


#
# Mix-ins
#


class Deletable(models.Model):
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class WithCreatedDateTime(models.Model):
    created = models.DateTimeField()

    def save(self, *args: List[any], **kwargs: Dict[str, any]):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(WithCreatedDateTime, self).save(*args, **kwargs)

    class Meta:
        abstract = True


#
# Models
#


class Lab(models.Model):
    pass


class Issue(Deletable, WithCreatedDateTime):
    state = models.CharField(max_length=10, choices=ISSUE_STATE_CHOICES, default=OPEN)
    title = models.CharField(max_length=MAX_TITLE_TEXT_LENGTH)
    description = models.CharField(max_length=MAX_BODY_TEXT_LENGTH, default="")
    number = models.IntegerField(default=1, editable=False)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name="issues")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["number", "lab"], name="issue_unique_number_in_lab"
            ),
            models.CheckConstraint(
                check=models.Q(number__gte=1), name="issue_number_gte_1"
            ),
        ]

    @classmethod
    def generate_number(cls, sender, instance, **kwargs) -> int:
        if not instance.pk:
            try:
                instance.number = (
                    cls.objects.filter(lab=instance.lab).order_by("-number")[0].number
                    + 1
                )
            except IndexError:
                pass


class IssueDescriptionHistoryItem(WithCreatedDateTime):
    state = models.CharField(max_length=10, choices=ISSUE_STATE_CHOICES, editable=False)
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="description_history",
        editable=False,
    )


class IssueStateHistoryItem(WithCreatedDateTime):
    state = models.CharField(max_length=10, choices=ISSUE_STATE_CHOICES, editable=False)
    issue = models.ForeignKey(
        Issue, on_delete=models.CASCADE, related_name="state_history"
    )


class IssueComment(Deletable, WithCreatedDateTime):
    body = models.CharField(max_length=MAX_BODY_TEXT_LENGTH)
    issue = models.ForeignKey(
        Issue, on_delete=models.CASCADE, related_name="comments"
    )


class IssueCommentHistoryItem(WithCreatedDateTime):
    body = models.CharField(max_length=MAX_BODY_TEXT_LENGTH, editable=False)
    comment = models.ForeignKey(
        IssueComment, on_delete=models.CASCADE, related_name="history"
    )


class Experiment(Deletable, WithCreatedDateTime):
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    COMMITTED = "COMMITTED"
    STATE_CHOICES = [
        (INACTIVE, "Inactive"),
        (ACTIVE, "Active"),
        (COMMITTED, "Committed"),
    ]
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default=INACTIVE)
    title = models.CharField(max_length=MAX_TITLE_TEXT_LENGTH)
    issues = models.ManyToManyField(Issue, related_name="experiments")
    terms = models.CharField(max_length=MAX_BODY_TEXT_LENGTH)
    end_date = models.DateField()
    number = models.IntegerField(editable=False)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name="experiments")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["number", "lab"], name="experiment_unique_number_in_lab"
            ),
            models.CheckConstraint(
                check=models.Q(number__gte=1), name="experiment_number_gte_1"
            ),
        ]


class ExperimentTermsHistoryItem(WithCreatedDateTime):
    body = models.CharField(max_length=MAX_BODY_TEXT_LENGTH, editable=False)
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name="terms_history",
        editable=False,
    )


class ExperimentEndDateHistoryItem(WithCreatedDateTime):
    end_date = models.DateField(editable=False)
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name="end_date_history",
        editable=False,
    )


pre_save.connect(Issue.generate_number, sender=Issue)
