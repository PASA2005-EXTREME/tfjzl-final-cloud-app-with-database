from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from . import models
from .models import Course, Enrollment, Question, Choice, Submission
import logging

logger = logging.getLogger(__name__)


def get_enrollement(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    try:
        enrollment = Enrollment.objects.get(user=user, course=course)
        return enrollment
    except Enrollment.DoesNotExist:
        return None


class CourseListView(generic.ListView):
    model = Course
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = Enrollment.objects.filter(
        user=user,
        course=course
    ).exists()

    if not is_enrolled and user.is_authenticated:
        Enrollment.objects.create(
            user=user,
            course=course,
            date_enrolled=timezone.now(),
        )
        return HttpResponseRedirect(
            reverse('onlinecourse:course_details',
                    args=(course.id,)))

    return HttpResponseRedirect(
        reverse('onlinecourse:course_details',
                args=(course.id,)))


def submit(request, course_id):
    """Handle exam submission for a course."""
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_enrollement(request, course_id)

    if not enrollment:
        return HttpResponseRedirect(
            reverse('onlinecourse:course_details',
                    args=(course_id,)))

    submission = Submission.objects.create(enrollment=enrollment)

    selected_ids = request.POST.getlist('choice')

    selected_choices = Choice.objects.filter(
        id__in=selected_ids
    )

    submission.choices.set(selected_choices)
    submission.save()

    return HttpResponseRedirect(
        reverse('onlinecourse:show_exam_result',
                args=(course_id, submission.id)))


def show_exam_result(request, course_id, submission_id):
    """Display the exam result for a submission."""
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    selected_choices = submission.choices.all()

    total_score = 0
    earned_score = 0

    questions = Question.objects.filter(course=course)

    for question in questions:
        total_score += question.grade
        selected_ids = selected_choices.filter(
            question=question
        ).values_list('id', flat=True)

        if question.is_get_score(selected_ids):
            earned_score += question.grade

    percentage = (earned_score / total_score * 100) if total_score > 0 else 0

    context = {
        'course': course,
        'submission': submission,
        'selected_choices': selected_choices,
        'earned_score': earned_score,
        'total_score': total_score,
        'percentage': percentage,
        'passed': percentage >= 80,
    }

    return render(request,
                  'onlinecourse/exam_result_bootstrap.html',
                  context)
