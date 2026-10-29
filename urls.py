from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'onlinecourse'

urlpatterns = [
    # Route to list all courses
    path(route='', view=views.CourseListView.as_view(), name='index'),

    # Route to course details page
    path(route='course/<int:pk>/',
         view=views.CourseDetailView.as_view(),
         name='course_details'),

    # Route to enroll in a course
    path(route='enroll/<int:course_id>/',
         view=views.enroll,
         name='enroll'),

    # Route to submit exam
    path(route='course/<int:course_id>/submit/',
         view=views.submit,
         name='submit'),

    # Route to show exam result
    path(route='course/<int:course_id>/submission/<int:submission_id>/result/',
         view=views.show_exam_result,
         name='show_exam_result'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
