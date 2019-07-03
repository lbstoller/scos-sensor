from django.db import models
from jsonfield import JSONField

from .task_result import TaskResult


class Acquisition(models.Model):
    """The data and metadata associated with a task.

    Task Result maps the acquisition to a specific task on the sensor, while
    recording ID allows for a single task to create more than one SigMF
    recording.

    It is an error to create more than one Acquisition associated with the same
    task result with the same recording id.

    """

    task_result = models.ForeignKey(
        TaskResult,
        on_delete=models.CASCADE,
        related_name="data",
        help_text="The task_result relative to the acquisition",
    )
    recording_id = models.IntegerField(
        default=0, help_text="The id of the recording relative to the task"
    )
    metadata = JSONField(help_text="The sigmf meta data for the acquisition")
    data = models.FileField(upload_to="blob/%Y/%m/%d/%H/%M/%S", null=True)

    class Meta:
        db_table = "acquisitions"
        ordering = ("task_result", "recording_id")
        unique_together = (("task_result", "recording_id"),)

    def __str__(self):
        return "{}/{}:{}".format(
            self.task_result.schedule_entry.name,
            self.task_result.task_id,
            self.recording_id,
        )
