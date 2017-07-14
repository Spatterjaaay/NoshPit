from django import forms

class PitForm(forms.Form):
       distance = forms.IntegerField(label='Distance', min_value=500, max_value=5000)
       # any validation for no past date? 
       deadline = forms.DateTimeField(label='Deadline')
