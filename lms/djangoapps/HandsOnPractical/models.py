import datetime

from django.db import models
from model_utils.models import TimeStampedModel
from opaque_keys.edx.django.models import CourseKeyField

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class CoursePracticalDate(TimeStampedModel):
    courseoverview = models.OneToOneField(CourseOverview, db_index=True, on_delete=models.CASCADE, default='course-v1:edX+DemoX+Demo_Course')

    def __str__(self):
        return self.courseoverview.display_name


class FormFillingDate(TimeStampedModel):
    courseoverview = models.ForeignKey(CoursePracticalDate, db_index=True, on_delete=models.CASCADE, default='course-v1:edX+DemoX+Demo_Course')
    practical_name = models.CharField(max_length=50, default='Practical')
    practical_description = models.TextField(max_length=250, default='description of practical')
    maximum_students = models.IntegerField(verbose_name='Maximum Students', default=100)
    venue = models.TextField(verbose_name='Venue', max_length=250, default='venue of practical')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.practical_name

    def show_form(self):
        """
        Returns True if students are allowed to fill the form 
        otherwise returns false

        based on return value form will be displayed
        """
        if self.start_date.date() <= datetime.datetime.now().date() and self.end_date.date() >= datetime.datetime.now().date():
            return True
        else:
            return False


class StudentConsultationList(TimeStampedModel):
    practical_name = models.ForeignKey(FormFillingDate, on_delete=models.CASCADE, default='1')
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=10)
    contact_name = models.CharField(max_length=50)
    contact_phone_number = models.CharField(max_length=10)
    other_requirements = models.TextField(max_length=200, blank=True)
    other_comments = models.TextField(max_length=200, blank=True)
