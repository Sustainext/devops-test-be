from django import forms
from datametric.models import FieldGroup, Path

class FieldGroupAdminForm(forms.ModelForm):
    class Meta:
        model = FieldGroup
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(FieldGroupAdminForm, self).__init__(*args, **kwargs)
        # Exclude Path instances that are already linked to a FieldGroup
        self.fields['path'].queryset = Path.objects.exclude(id__in=FieldGroup.objects.values('path_id'))