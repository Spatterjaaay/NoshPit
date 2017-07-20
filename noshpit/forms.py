from django import forms

class PitForm(forms.Form):
    distance = forms.IntegerField(label='Distance', min_value=500, max_value=5000)
       # any validation for no past date?
       # location
class JoinForm(forms.Form):
    token = forms.CharField(label='Token', min_length=5, max_length=5)
