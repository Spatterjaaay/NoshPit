from django import forms

class PitForm(forms.Form):
    distance = forms.IntegerField(label='Distance', min_value=500, max_value=5000, widget=forms.TextInput(attrs={'placeholder': 'Enter Distance in m', 'class': 'form-control col-sm-5'}))

class JoinForm(forms.Form):
    token = forms.CharField(label='Token', min_length=5, max_length=5, widget=forms.TextInput(attrs={'placeholder': 'Enter Token', 'class': 'form-control col-sm-3'}))

class EmailForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Enter Email', 'class': 'form-control col-sm-5','id': 'inputEmail3'}))
