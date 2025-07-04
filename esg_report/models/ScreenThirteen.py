from django.db import models
from common.models.AbstractModel import AbstractModel
from common.models.HistoricalModel import HistoricalModelMixin
from sustainapp.models import Report


class ScreenThirteen(AbstractModel, HistoricalModelMixin):
    """
    Model for Screen Thirteen of ESG Report
    """

    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name="screen_thirteen"
    )
    employee_policies_statement = models.JSONField(
        verbose_name="Employee Policies Statement",
        help_text="Statement about company's employees and their policies",
        blank=True,
        null=True,
    )

    workforce_hire_retention_statement = models.JSONField(
        verbose_name="Workforce Hire and Retention Statement",
        help_text="Statement about company's workforce hire and retention strategies",
        blank=True,
        null=True,
    )

    standard_wage = models.JSONField(
        verbose_name="Standard Wage",
        help_text="Information about the company's standard wage policies",
        blank=True,
        null=True,
    )

    performance_review_process = models.JSONField(
        verbose_name="Performance Review Process",
        help_text="Statement about company's process for performance review of employees",
        blank=True,
        null=True,
    )

    forced_labor_position = models.JSONField(
        verbose_name="Position on Forced/Compulsory Labor",
        help_text="Statement about company's position on forced or compulsory labor",
        blank=True,
        null=True,
    )

    child_labor_position = models.JSONField(
        verbose_name="Position on Child Labor",
        help_text="Statement about company's position on child labor",
        blank=True,
        null=True,
    )

    employee_diversity_position = models.JSONField(
        verbose_name="Position on Employee Diversity",
        help_text="Statement about company's position on diversity of employees",
        blank=True,
        null=True,
    )

    employee_skill_upgrade_programs = models.JSONField(
        verbose_name="Employee Skill Upgrade Programs",
        help_text="Statement about company's programs for upgrading employee's skills",
        blank=True,
        null=True,
    )

    remuneration_practices = models.JSONField(
        verbose_name="Remuneration Practices and Policies",
        help_text="Statement about company's remuneration practices and policies",
        blank=True,
        null=True,
    )

    ohs_policies = models.JSONField(
        verbose_name="Occupational Health and Safety Policies",
        help_text="Statement about company's Occupational Health and Safety (OHS) policies",
        blank=True,
        null=True,
    )

    hazard_risk_assessment = models.JSONField(
        verbose_name="Hazard and Risk Assessment Process",
        help_text="Statement about company's process of Hazard and risk assessment",
        blank=True,
        null=True,
    )

    work_related_health_injuries = models.JSONField(
        verbose_name="Work-Related Ill Health and Injuries",
        help_text="Statement about work-related ill health and injuries in the company",
        blank=True,
        null=True,
    )

    # New fields
    safety_training = models.JSONField(
        verbose_name="Safety Training",
        help_text="Statement about the company's safety training programs for employees",
        blank=True,
        null=True,
    )

    ohs_management_system = models.JSONField(
        verbose_name="OHS Management System",
        help_text="Statement about the company's Occupational Health and Safety (OHS) management system",
        blank=True,
        null=True,
    )

    freedom_of_association_views = models.JSONField(
        verbose_name="Views on Freedom of Association and Collective Bargaining",
        help_text="Statement about the company's views on freedom of association and collective bargaining",
        blank=True,
        null=True,
    )

    violation_discrimination_policy = models.JSONField(
        verbose_name="Policy on Addressing Violation/Discrimination",
        help_text="Statement about the company's policy for addressing violation or discrimination",
        blank=True,
        null=True,
    )

    indigenous_rights_policy = models.JSONField(
        verbose_name="Policy on Violation of Indigenous People's Rights",
        help_text="Statement about the company's policy on violation of the rights of indigenous people",
        blank=True,
        null=True,
    )

    parental_leaves = models.JSONField(
        verbose_name="Dynamic Question Answer",
        help_text="This field stores the answer to a dynamic question provided as input",
        blank=True,
        null=True,
    )
    security_personnel_internal_training = models.JSONField(
        verbose_name="Percentage of Security Personnel Who Have Received Formal Training in the Organisation",
        help_text="Percentage of security personnel who have received formal training in the organisation",
        blank=True,
        null=True,
    )
    security_personnel_external_training = models.JSONField(
        verbose_name="Percentage of Security Personnel Who Have Received Formal Training from Third-Party Organisation",
        help_text="Percentage of security personnel who have received formal training from third-party organisation",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "screen_thirteen"
