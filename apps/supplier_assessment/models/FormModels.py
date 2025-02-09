from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from materiality_dashboard.models import MaterialTopic, Disclosure
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


class Form(AbstractModel, HistoricalModelMixin):
    """
    The `Form` model represents a form that can be filled out by users.
    Each form can have multiple `Question` objects, which represent the individual questions in the form.
    """

    title = models.CharField(max_length=255)


class Question(AbstractModel, HistoricalModelMixin):
    """
    The `Question` model stores the question text as a JSON field, as well as the type of the question (e.g. short text, long text, yes/no, multiple choice, etc.).
    Each question is associated with a `MaterialTopic` and optionally a `Disclosure`.
    """

    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    question = models.JSONField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    material_topic = models.ForeignKey(
        MaterialTopic, on_delete=models.CASCADE, related_name="questions"
    )
    disclosure = models.ForeignKey(
        Disclosure,
        on_delete=models.SET_NULL,
        related_name="questions",
        null=True,
        blank=True,
        default=None,
    )


class FileQuestion(AbstractModel, HistoricalModelMixin):
    """
    The `FileQuestion` model is used to associate a file with a particular question.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    file = models.FileField(upload_to="question_files/")


class Answer(AbstractModel, HistoricalModelMixin):
    """
    The `Answer` model stores the user's response to a question, which is also stored as a JSON field.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.JSONField()
    answer_type = models.CharField(max_length=20, choices=QUESTION_TYPES)


class FileAnswer(AbstractModel, HistoricalModelMixin):
    """
    The `FileAnswer` model is used to associate a file with a particular answer.
    """

    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    file = models.FileField(upload_to="answer_files/")
