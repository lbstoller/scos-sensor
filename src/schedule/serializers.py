from datetime import datetime

from rest_framework import serializers
from rest_framework.reverse import reverse

import actions
from sensor import V1
from sensor.utils import (
    get_datetime_from_timestamp,
    get_timestamp_from_datetime
)
from .models import ScheduleEntry


def datetimes_to_timestamps(validated_data):
    """Covert datetimes to timestamp integers in validated_data."""
    for k, v in validated_data.items():
        if type(v) is datetime:
            validated_data[k] = get_timestamp_from_datetime(v)

    return validated_data


class DateTimeFromTimestampField(serializers.DateTimeField):
    """DateTimeField with integer timestamp as internal value."""
    def to_representation(self, ts):
        """Convert integer timestamp to an ISO 8601 datetime string."""
        if ts is None:
            return None

        dt = get_datetime_from_timestamp(ts)
        dt_str = super(DateTimeFromTimestampField, self).to_representation(dt)

        return dt_str

    def to_internal_value(self, dt_str):
        """Parse an ISO 8601 datetime string and return a timestamp integer."""
        if dt_str is None:
            return None

        dt = super(DateTimeFromTimestampField, self).to_internal_value(dt_str)
        return get_timestamp_from_datetime(dt)


class ScheduleEntrySerializer(serializers.HyperlinkedModelSerializer):
    acquisitions = serializers.SerializerMethodField(
        help_text="The list of acquisitions related to the entry"
    )
    results = serializers.SerializerMethodField(
        help_text="The list of results related to the entry"
    )
    start = DateTimeFromTimestampField(
        required=False,
        allow_null=True,
        default=None,
        help_text="UTC time (ISO 8601) to start, or leave blank for 'now'"
    )
    stop = DateTimeFromTimestampField(
        required=False,
        allow_null=True,
        default=None,
        label="Absolute stop",
        help_text=("UTC time (ISO 8601) to stop, "
                   "or leave blank for 'never' (not valid with relative stop)")
    )
    relative_stop = serializers.IntegerField(
        required=False,
        write_only=True,
        allow_null=True,
        default=None,
        min_value=1,
        help_text=("Integer seconds after start to stop, "
                   "or leave blank for 'never' (not valid with absolute stop)")
    )
    next_task_time = DateTimeFromTimestampField(
        read_only=True,
        help_text="UTC time (ISO 8601) the next task is scheduled for"
    )
    action = serializers.ChoiceField(
        choices=actions.CHOICES,
        help_text="[Required] The name of the action to be scheduled"
    )

    class Meta:
        model = ScheduleEntry
        fields = (
            'url',
            'name',
            'action',
            'priority',
            'start',
            'stop',
            'relative_stop',
            'interval',
            'is_active',
            'is_private',
            'callback_url',
            'next_task_time',
            'next_task_id',
            'created',
            'modified',
            'owner',
            'acquisitions',
            'results'
        )
        extra_kwargs = {
            'url': {
                'view_name': 'schedule-detail',
                'help_text': "The url of the entry"
            },
            'owner': {
                'view_name': 'user-detail',
                'help_text': "The name of the user who owns the entry"
            }
        }
        read_only_fields = ('is_active', 'next_task_time')
        write_only_fields = ('relative_stop',)

    def validate(self, data):
        """Do object-level validation."""

        if 'start' in data and data['start'] is None:
            data.pop('start')

        got_absolute_stop = False
        got_relative_stop = False

        if 'stop' in data and data['stop'] is not None:
            got_absolute_stop = True

        if 'relative_stop' in data and data['relative_stop'] is not None:
            got_relative_stop = True

        if got_absolute_stop and got_relative_stop:
            err = "pass only one of stop and relative_stop"
            raise serializers.ValidationError(err)

        return data

    def get_acquisitions(self, obj):
        request = self.context['request']
        kws = {'schedule_entry_name': obj.name}
        kws.update(V1)
        return reverse('acquisition-list', kwargs=kws, request=request)

    def get_results(self, obj):
        request = self.context['request']
        kws = {'schedule_entry_name': obj.name}
        kws.update(V1)
        return reverse('result-list', kwargs=kws, request=request)

    def to_internal_value(self, data):
        """Clean up input before starting validation."""
        # Allow 'absolute_stop' to be a synonym for 'stop'
        if 'absolute_stop' in data:
            data['stop'] = data.pop('absolute_stop')

        # py2.7 compat -> super().to_internal...
        return super(ScheduleEntrySerializer, self).to_internal_value(data)
