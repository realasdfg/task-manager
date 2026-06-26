from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def get_absolute_url(self):
        return reverse("tasks:position-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workers"
    )

    class Meta:
        verbose_name = "worker"
        verbose_name_plural = "workers"

    def get_absolute_url(self):
        return reverse("tasks:worker-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(
        get_user_model(),
        related_name="teams",
        blank=True
    )

    def get_absolute_url(self):
        return reverse("tasks:team-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    teams = models.ManyToManyField(
        Team,
        related_name="projects",
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse("tasks:project-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class TaskType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def get_absolute_url(self):
        return reverse("tasks:tasktype-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Task(models.Model):
    class Priority(models.TextChoices):
        URGENT = "urgent", "Urgent"
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=10,
        choices=Priority,
        default=Priority.MEDIUM
    )
    task_type = models.ForeignKey(
        TaskType,
        on_delete=models.PROTECT,
        related_name="tasks"
    )
    assignees = models.ManyToManyField(
        get_user_model(),
        related_name="tasks",
        blank=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse("tasks:task-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name
