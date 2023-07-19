from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.core.exceptions import ValidationError

from comparisons.models import Species, ComparisonTool, Dashboard


class NewComparisonForm(forms.Form):
    species = forms.ModelChoiceField(Species.objects.all(), label='Select species:')
    tool = forms.ModelChoiceField(ComparisonTool.objects.all(), label='Select cgMLST tool and version:')
    sequences = SimpleArrayField(forms.CharField(), delimiter=" ", label='Sequences (ids delimited by space)')

    def clean_sequences(self):
        data = self.cleaned_data["sequences"]
        for item in data:
            if item == "UTYUTYRR":
                raise ValidationError("You have forgotten about Fred!")

        return data


class DeleteDatasetForm(forms.Form):
    confirm_name = forms.CharField(max_length=40, label='To delete dataset, confirm dataset name')


class NewDashboardForm(forms.ModelForm):
    class Meta:
        model = Dashboard
        fields = ['tbr_data_fields', 'lims_data_fields']