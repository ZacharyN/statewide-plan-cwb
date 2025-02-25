# core/plan_work/models.py
"""
The Plan Work module contains the elements of the Statewide Plan for Community Well-Being.
The Statewide Plan has 4 Goals. Each Goal has several Objectives. Each Objective has multiple Strategies.
Plan Actors, those who will work toward achieving the goals of this plan, have Action Steps or Commitments
the detail how they will advance one of the Strategies on the Plan.

Goals, Objectives, Strategies, and Action Steps/Commitments are links to run reports easily.
For example, under this relationship scheme, it is possible to filter all the Nebraska Children's teams with
Action Steps related to a specific Goal, Objective, or Strategy.
"""

import uuid
from django.db import models
from smart_selects.db_fields import ChainedForeignKey
from core.plan_actors.models import NcffTeam
from core.standardization import ActivityStatusChoice, Quarters, Years
from core.plan_actors import CommunityCollaborative
from core.plan_actors import SystemPartner
from django.conf import settings


class Goal(models.Model):
    goal_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal_number = models.IntegerField()
    goal_name = models.CharField(max_length=255)

    def __str__(self):
        return f"Goal: {self.goal_number} - {self.goal_name}"

    class Meta:
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'
        db_table = 'goal'
        ordering = ('goal_number',)


class Objective(models.Model):
    objective_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    objective_number = models.IntegerField()
    objective_name = models.CharField(max_length=255)
    related_goal = models.ForeignKey('Goal', on_delete=models.CASCADE)

    def __str__(self):
        return f"Goal {self.related_goal.goal_number}, Obj {self.objective_number} - {self.objective_name}"

    class Meta:
        verbose_name = 'Objective'
        verbose_name_plural = 'Objectives'
        db_table = 'objective'
        ordering = ('related_goal', 'objective_number',)


class Strategy(models.Model):
    strategy_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strategy_number = models.CharField(max_length=9, help_text="Automatically generated. No need to set manually.")
    strategy_name = models.CharField(max_length=255)
    related_goal = models.ForeignKey('Goal', on_delete=models.CASCADE)
    related_objective = ChainedForeignKey(
        Objective,
        chained_field="related_goal",  # The field in this model to chain from.
        chained_model_field="related_goal",  # The field in Objective model that relates to Goal.
        show_all=False,
        auto_choose=True,
        sort=True,
    )

    # Functionality that increments the strategy number is the STRG-XXXX format.
    def save(self, *args, **kwargs):
        if not self.strategy_number:
            prefix = "STRG-"
            last_strategy = Strategy.objects.order_by('strategy_number').last()

            if last_strategy:
                last_number = int(last_strategy.strategy_number.split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1000  # Start from 1000

            self.strategy_number = f"{prefix}{new_number}"
        super().save(*args, **kwargs)

    ncff_teams = models.ManyToManyField('NcffTeam', blank=True)
    system_partners = models.ManyToManyField('SystemPartner', blank=True)

    community_collaboratives = models.ManyToManyField(
        'CommunityCollaborative',
        through='core.CollaborativeStrategyPriority',
        blank=True
    )

    def __str__(self):
        return (f"Goal {self.related_goal.goal_number}, "
                f"Obj {self.related_objective.objective_number} | "
                f"Strategy {self.strategy_number} - {self.strategy_name}")

    class Meta:
        verbose_name = 'Strategy'
        verbose_name_plural = 'Strategies'
        db_table = 'strategy'
        ordering = ('related_goal', 'related_objective', 'strategy_number',)


class CommunityActionStep(models.Model):
    activity_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity_number = models.CharField(max_length=10, help_text="Automatically generated. No need to set manually.")
    activity_name = models.CharField(max_length=255)
    activity_details = models.TextField(max_length=1200)
    activity_lead = models.CharField(max_length=100,
                                     help_text="Indicate who will lead the activity (person or organization).",
                                     blank=True, default="")
    activity_status = models.CharField(max_length=25, choices=ActivityStatusChoice.choices)
    completedby_year = models.CharField(max_length=4, choices=Years.choices, blank=True)
    completedby_quarter = models.CharField(max_length=3, choices=Quarters.choices, blank=True)
    community_creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_community_action_steps',  # unique related_name
        null=True
    )
    related_collaborative = models.ForeignKey(CommunityCollaborative, on_delete=models.CASCADE)
    related_goal = models.ForeignKey('Goal', on_delete=models.SET_NULL, null=True, blank=True)
    related_objective = ChainedForeignKey(
        'Objective',
        chained_field="related_goal",
        chained_model_field="related_goal",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    related_strategy = ChainedForeignKey(
        'Strategy',
        chained_field="related_objective",
        chained_model_field="related_objective",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.activity_number:
            prefix = "C-ACT-"
            last_activity = CommunityActionStep.objects.order_by('activity_number').last()

            if last_activity:
                # Splitting the string to extract the numeric part
                number_part = last_activity.activity_number.split('-')[2]
                last_number = int(number_part)  # Converting the extracted part to an integer
                new_number = last_number + 1
            else:
                new_number = 1000  # Start from 1000

            self.activity_number = f"{prefix}{new_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        collab_name = (self.related_collaborative.community_collab_short_name or
                       self.related_collaborative.community_collab_name)
        return (f"[{self.related_collaborative.community_collab_short_name}] - Goal {self.related_goal}, "
                f"Objective {self.related_objective}, Strategy {self.related_strategy}")

    class Meta:
        verbose_name_plural = 'Community Action Step'
        verbose_name = 'Community Action Steps'
        db_table = 'community_actionstep'
        ordering = ['related_collaborative', 'related_goal', 'related_objective', 'related_strategy',
                    'activity_status', 'completedby_year']


class NCActionStep(models.Model):
    activity_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity_number = models.CharField(max_length=15, blank=True, null=True,
                                       help_text="Automatically generated. No need to set manually.")
    activity_name = models.CharField(max_length=255)
    activity_details = models.TextField(max_length=1500)
    activity_lead = models.CharField(max_length=100,
                                     help_text="Indicate who will lead the activity (person, organization, or team).",
                                     blank=True, default="")
    activity_priority = models.BooleanField()
    activity_status = models.CharField(max_length=25, choices=ActivityStatusChoice.choices)
    completedby_year = models.CharField(max_length=4, choices=Years.choices)
    completedby_quarter = models.CharField(max_length=3, choices=Quarters.choices)
    ncff_team = models.ForeignKey(NcffTeam, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="action_steps")
    nc_staff_creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_nc_action_steps',  # unique related_name
        null=True
    )
    related_goal = models.ForeignKey('Goal', on_delete=models.SET_NULL, null=True, blank=True)
    related_objective = ChainedForeignKey(
        'Objective',
        chained_field="related_goal",
        chained_model_field="related_goal",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    related_strategy = ChainedForeignKey(
        'Strategy',
        chained_field="related_objective",
        chained_model_field="related_objective",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.activity_number:
            prefix = "NC-ACT-"
            last_activity = NCActionStep.objects.filter(activity_number__startswith=prefix).order_by(
                '-activity_number').first()

            if last_activity and last_activity.activity_number:
                last_number = int(last_activity.activity_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1000  # Start from 1000

            self.activity_number = f"{prefix}{new_number:04d}"  # Ensure consistent 4-digit numbering
        super().save(*args, **kwargs)

    def __str__(self):
        return (f"Goal {self.related_goal.goal_number}, Obj. {self.related_objective.objective_number}, "
                f"Strategy {self.related_strategy.strategy_number}")

    class Meta:
        verbose_name = "NC Action Step"
        verbose_name_plural = "NC Action Steps"
        db_table = 'nc_actionstep'
        ordering = ['related_goal', 'related_objective', 'related_strategy', 'activity_number', 'completedby_year',]


class SystemPartnerCommitment(models.Model):
    commitment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commitment_number = models.CharField(max_length=12, null=True, blank=True,
                                         help_text="Automatically generated. No need to set manually.")
    commitment_name = models.CharField(max_length=255)
    commitment_details = models.TextField(max_length=1500)
    commitment_lead = models.CharField(max_length=100,
                                       help_text="Indicate who will lead the commitment (person, organization, "
                                                 "or team).",
                                       blank=True, default="")
    commitment_status = models.CharField(max_length=25, choices=ActivityStatusChoice.choices)
    completedby_year = models.CharField(max_length=4, choices=Years.choices)
    completedby_quarter = models.CharField(max_length=3, choices=Quarters.choices)
    system_partner_creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_system_partner_commitments',  # unique related_name
        null=True,
        blank=True
    )
    related_systempartner = models.ForeignKey(SystemPartner, on_delete=models.CASCADE)
    related_goal = models.ForeignKey('Goal', on_delete=models.SET_NULL, null=True, blank=True)
    related_objective = ChainedForeignKey(
        'Objective',
        chained_field="related_goal",
        chained_model_field="related_goal",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    related_strategy = ChainedForeignKey(
        'Strategy',
        chained_field="related_objective",
        chained_model_field="related_objective",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.commitment_number:
            prefix = "COMMIT-"
            last_commitment = SystemPartnerCommitment.objects.order_by('commitment_number').last()

            if last_commitment:
                number_part = last_commitment.commitment_number.split('-')[2]
                last_number = int(number_part)  # Converting extracted part to an integer
                new_number = last_number + 1
            else:
                new_number = 1000  # Start from 1000

            self.commitment_number = f"{prefix}{new_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return (f"System Partner: {self.related_systempartner.system_partner_short_name or self.related_systempartner.system_partner_name}, "
                f"Goal {self.related_goal.goal_number}, Obj. {self.related_objective.objective_number}, "
                f"Strategy {self.related_strategy.strategy_number}, Commitment #{self.commitment_number}")

    class Meta:
        verbose_name = "System Partner Commitment"
        verbose_name_plural = "System Partner Commitments"
        db_table = 'system_partner_commitments'
        ordering = ['related_systempartner', 'related_goal', 'related_objective', 'related_strategy',
                    'commitment_number', 'completedby_year']
