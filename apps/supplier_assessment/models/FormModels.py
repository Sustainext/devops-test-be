from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from materiality_dashboard.models import MaterialTopic, Disclosure
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.contrib.auth import get_user_model

User = get_user_model()

QUESTION_TYPES = [
    ("text_short", "Short Text"),
    ("text_long", "Long Text"),
    ("yes_no", "Yes/No"),
    ("multiple_choice", "Multiple Choice"),
    ("fill_blank", "Fill in the Blank"),
    ("multi_fill_blank", "Multiple Fill in Blanks"),
]


class PredefinedQuestion(AbstractModel, HistoricalModelMixin):
    """
    A question provided by the platform.
    """

    question = models.JSONField(
        help_text="The question content (e.g. text, options, etc.)"
    )
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    material_topic = models.ForeignKey(
        MaterialTopic, on_delete=models.CASCADE, related_name="predefined_questions"
    )
    disclosure = models.ForeignKey(
        Disclosure,
        on_delete=models.SET_NULL,
        related_name="predefined_questions",
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return f"Predefined: {self.question_type}"


class CustomQuestion(AbstractModel, HistoricalModelMixin):
    """
    A custom question created by a client admin.
    Stored independently so that the admin can reuse them in different forms.
    """

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="custom_questions"
    )
    question = models.JSONField(
        help_text="The custom question content (e.g. text, options, etc.)"
    )
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    material_topic = models.ForeignKey(
        MaterialTopic, on_delete=models.CASCADE, related_name="custom_questions"
    )
    disclosure = models.ForeignKey(
        Disclosure,
        on_delete=models.SET_NULL,
        related_name="custom_questions",
        null=True,
        blank=True,
        default=None,
    )


class Form(AbstractModel, HistoricalModelMixin):
    """
    A form that can include:
      - Predefined questions (selected from the global pool)
      - Custom questions (created by the admin)
    """

    title = models.CharField(max_length=255)
    predefined_questions = models.ManyToManyField(
        PredefinedQuestion, blank=True, related_name="forms"
    )
    custom_questions = models.ManyToManyField(
        CustomQuestion, blank=True, related_name="forms"
    )

    def __str__(self):
        return self.title

    @property
    def all_questions(self):
        """Returns the combined list of predefined and custom questions."""
        return list(self.predefined_questions.all()) + list(self.custom_questions.all())


class QuestionFile(AbstractModel, HistoricalModelMixin):
    """
    A generic file attachment for any question type.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    question = GenericForeignKey("content_type", "object_id")

    file = models.FileField(upload_to="question_files/")

    def __str__(self):
        return f"File attached to {self.content_type} (ID: {self.object_id})"


class Answer(AbstractModel, HistoricalModelMixin):
    """
    Stores the stakeholder's answer.
    Exactly one of predefined_question or custom_question must be set.
    """

    predefined_question = models.ForeignKey(
        PredefinedQuestion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="answers",
    )
    custom_question = models.ForeignKey(
        CustomQuestion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="answers",
    )
    answer = models.JSONField(
        help_text="The answer content (e.g. text, selected option, etc.)"
    )
    # Link to the submission (grouping answers per assessment submission)
    assessment_submission = models.ForeignKey(
        "AssessmentSubmission",
        on_delete=models.CASCADE,
        related_name="answers",
        null=True,
        blank=True,
    )

    def __str__(self):
        if self.predefined_question:
            return f"Answer for: {self.predefined_question}"
        elif self.custom_question:
            return f"Answer for: {self.custom_question}"
        return "Answer"

    def clean(self):
        from rest_framework.exceptions import ValidationError

        if (self.predefined_question and self.custom_question) or (
            not self.predefined_question and not self.custom_question
        ):
            raise ValidationError(
                "Exactly one of predefined_question or custom_question must be set."
            )


class FileAnswer(AbstractModel, HistoricalModelMixin):
    """
    The `FileAnswer` model is used to associate a file with a particular answer.
    """

    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    file = models.FileField(upload_to="answer_files/")
