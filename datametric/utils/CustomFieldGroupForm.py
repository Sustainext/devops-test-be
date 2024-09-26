from django import forms
from datametric.models import FieldGroup, Path


class FieldGroupAdminForm(forms.ModelForm):
    """
    The `FieldGroupAdminForm` class is used to create and update `FieldGroup` instances in the admin interface. 
    It handles the logic for filtering the available `Path` choices based on whether the `FieldGroup` instance is new or being edited.

    When creating a new `FieldGroup`, the form will exclude all `Path` instances that are already linked to another `FieldGroup`. 
    When editing an existing `FieldGroup`, the form will exclude `Path` instances that are linked to other `FieldGroups`, 
    but include the `Path` instance that is linked to the current `FieldGroup` being edited.
    """

    class Meta:
        model = FieldGroup
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(FieldGroupAdminForm, self).__init__(*args, **kwargs)

        # Check if we're editing an existing FieldGroup instance
        if self.instance and self.instance.pk:
            # Exclude paths linked to other FieldGroups, but include the one linked to the current instance
            self.fields["path"].queryset = Path.objects.exclude(
                id__in=FieldGroup.objects.exclude(pk=self.instance.pk).values("path_id")
            )
        else:
            # If it's a new instance, exclude all paths already linked to a FieldGroup
            self.fields["path"].queryset = Path.objects.exclude(
                id__in=FieldGroup.objects.values("path_id")
            )
