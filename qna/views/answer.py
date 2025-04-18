from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView, View

from qna.forms import AnswerForm
from qna.models import Answer, Question


class AnswerCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    View for creating answers
    """

    model = Answer
    form_class = AnswerForm
    template_name = "qna/question_detail.html"
    success_message = "Your answer has been posted!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["question"] = get_object_or_404(Question, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        question = get_object_or_404(Question, pk=self.kwargs["pk"])

        # Check if the user is trying to answer their own question
        if self.request.user == question.author:
            form.add_error(None, "You cannot answer your own question.")
            return self.form_invalid(form)

        form.instance.author = self.request.user
        form.instance.question = question
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("question_detail", kwargs={"pk": self.kwargs["pk"]})


class AnswerUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    View for updating answers
    """

    model = Answer
    form_class = AnswerForm
    template_name = "qna/update_answer.html"
    success_message = "Your answer has been updated!"

    def get_queryset(self):
        return Answer.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy("question_detail", kwargs={"pk": self.object.question.pk})


class AnswerDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    View for deleting answers
    """

    model = Answer
    template_name = "qna/delete_answer.html"
    success_message = "Your answer has been deleted!"

    def get_queryset(self):
        return Answer.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy("question_detail", kwargs={"pk": self.object.question.pk})


class LikeAnswerView(LoginRequiredMixin, View):
    """
    View for liking and unliking answers
    """

    def post(self, request, *args, **kwargs):
        answer = get_object_or_404(Answer, pk=self.kwargs["pk"])
        question_pk = answer.question.pk

        if request.user in answer.likes.all():
            answer.likes.remove(request.user)
            messages.success(request, "You unliked this answer!")
        else:
            answer.likes.add(request.user)
            messages.success(request, "You liked this answer!")

        return redirect(reverse_lazy("question_detail", kwargs={"pk": question_pk}))
