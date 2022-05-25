import datetime
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import generic
from rest_framework import response, status, viewsets

from lms.djangoapps.course_api.views import CourseListView
from lms.djangoapps.HandsOnPractical.models import CoursePracticalDate, FormFillingDate, StudentConsultationList
from lms.djangoapps.HandsOnPractical.serializers import StudentConsultationListSerializer
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

log = logging.getLogger("edx.courseware")


class StudentRegistrationForm(LoginRequiredMixin, generic.TemplateView):

    """
    To display registration form
    """
    template_name = 'courseware/student_registration_form.html'

    def get_context_data(self, **kwargs):
        context = super(StudentRegistrationForm, self).get_context_data(**kwargs)

        try:
            practical_course = CoursePracticalDate.objects.filter(courseoverview=kwargs['course_id']).values()
            queryset = FormFillingDate.objects.filter(courseoverview=practical_course[0].get('id'))
        except:
            queryset = None

        course = CourseOverview.get_from_id(kwargs['course_id'])
        context.update({'course_id': kwargs['course_id'], 'course': course, 'queryset': queryset})

        return context


class EventsCalendarView(LoginRequiredMixin, generic.TemplateView):
    """
    To display Full calendar js template
    """
    template_name = 'courseware/Events_details.html'

    def get_context_data(self, **kwargs):
        context = super(EventsCalendarView, self).get_context_data(**kwargs)

        course = CourseOverview.get_from_id(kwargs['course_id'])
        context.update({'course_id': kwargs['course_id'], 'course': course})
        return context


class StudentRegistrationAPI(viewsets.ModelViewSet):
    """
    def create: To check if user has entered valid data and to send mail regarding the session also
    def list: to check if user has already registered or not and return the data
    """

    queryset = StudentConsultationList.objects.all()
    serializer_class = StudentConsultationListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            practical_detais = FormFillingDate.objects.get(pk=serializer.data.get('practical_name'))
            template = 'emails/email.html'
            message = render_to_string(template, {
                "user": request.user.first_name,
                "practical_name": practical_detais.practical_name,
                "start_date": practical_detais.start_date,
                "end_date": practical_detais.end_date,
                "start_time": str(practical_detais.start_date.time()),
                "end_time": str(practical_detais.end_date.time()),
                "venue": practical_detais.venue
            })
            email = EmailMultiAlternatives('Hands On Practical', message, from_email=settings.EMAIL_HOST_USER, to=[serializer.data.get('email')])
            email.attach_alternative(message, "text/html")
            email.send()
        else:
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        user_exist_flag = False          # flag that returns true if user has already registered for the session
        seats_fulled = False             # flag that returns true if seat are fulled in practical

        email = request.GET.get("email")
        practical_name = request.GET.get("practical_name")

        user_exist_data = list(self.queryset.filter(email=email, practical_name=practical_name).values())

        student_count = self.queryset.filter(practical_name=practical_name).count()
        practical_data = FormFillingDate.objects.get(id=practical_name)

        if user_exist_data:
            user_exist_flag = True

        if student_count == practical_data.maximum_students:
            seats_fulled = True

        return response.Response({"user_exist_data": user_exist_flag, "seats_fulled": seats_fulled})


class DisplayCoursesListAPI(viewsets.ModelViewSet):
    """
    These class returns the Course List data that needs to be displayed in Full calendar js
    Here, only necessary data is returned and in formatted manner that is understanded by Full calendar js
    """

    def list(self, request, *args, **kwargs):
        """
        To return the Practical list for the given course which is to be displayed in full calendar
        """

        try:
            course = CoursePracticalDate.objects.filter(courseoverview=kwargs.get('course_id')).values()
            all_data = FormFillingDate.objects.filter(courseoverview=course[0].get('id'))
        except:
            log.error("No Data retrieved")
            all_data = None

        all_practical_list = []
        if all_data:
            for i in all_data:
                practical_list = {}
                practical_dates = "Start Date:" + i.start_date.date().strftime("%d-%m-%Y") + " " + "End Date:" + i.end_date.date().strftime("%d-%m-%Y")
                practical_list['title'] = i.practical_name
                practical_list['start'] = datetime.datetime.strptime(str(i.start_date.date()), "%Y-%m-%d").strftime("%Y-%m-%d")
                practical_list['end'] = datetime.datetime.strptime(str(i.end_date.date()), "%Y-%m-%d").strftime("%Y-%m-%d")
                practical_list['description'] = practical_dates + "<br> Venue: " + i.venue + "<br>" + i.practical_description
                practical_list['url'] = reverse('practical_registration_form', kwargs={'course_id': kwargs.get('course_id')})
                all_practical_list.append(practical_list)

        return response.Response(all_practical_list)


class DisplayMaximumStudent(viewsets.ModelViewSet):
    """
    These class returns the "Maximum Student Number" that needs to be displayed in Full calendar js
    Here, only necessary data is returned and in formatted manner that is understanded by Full calendar js
    """

    def list(self, request, *args, **kwargs):
        try:
            course = CoursePracticalDate.objects.filter(courseoverview=kwargs.get('course_id')).values()
            all_data = FormFillingDate.objects.filter(courseoverview=course[0].get('id'))
        except:
            log.error("No Data retrieved")
            all_data = None

        all_practical_list = []
        if all_data:
            for i in all_data:
                practical_list = {}
                practical_list['title'] = "Number of Seats left: " + str(i.maximum_students - StudentConsultationList.objects.filter(practical_name=i.id).count())
                practical_list['start'] = datetime.datetime.strptime(str(i.start_date.date()), "%Y-%m-%d").strftime("%Y-%m-%d")
                practical_list['end'] = datetime.datetime.strptime(str(i.end_date.date()), "%Y-%m-%d").strftime("%Y-%m-%d")
                all_practical_list.append(practical_list)

        return response.Response(all_practical_list)
