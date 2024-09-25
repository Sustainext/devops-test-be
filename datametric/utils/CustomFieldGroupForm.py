from django import forms
from datametric.models import FieldGroup, Path

class FieldGroupAdminForm(forms.ModelForm):
    class Meta:
        model = FieldGroup
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(FieldGroupAdminForm, self).__init__(*args, **kwargs)
        
        # Check if we're editing an existing FieldGroup instance
        if self.instance and self.instance.pk:
            # Exclude paths linked to other FieldGroups, but include the one linked to the current instance
            self.fields['path'].queryset = Path.objects.exclude(
                id__in=FieldGroup.objects.exclude(pk=self.instance.pk).values('path_id')
            )
        else:
            # If it's a new instance, exclude all paths already linked to a FieldGroup
            self.fields['path'].queryset = Path.objects.exclude(
                id__in=FieldGroup.objects.values('path_id')
            )
