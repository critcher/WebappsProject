from jsonValidation import *
import os
from framework.forms import AppSettingsForm
from django import forms
from django.conf import settings
import datetime

FORM_SCHEMA_FILE = os.path.join(settings.PROJECT_ROOT, '../framework/static/formSchema.json')

""" Throws IOError if the file is invalid, and ValueError
    if the json is invalid.
"""
def getSchemaFromFile(filename):
    with open(filename, 'r') as f:
        schemaText = f.read()
        schemaDict = json.loads(schemaText)
    return schemaDict

""" Throws ValueError if the json is invalid, and
    ValidationError if the json does not fit the schema.
"""
def validateFromString(schema, jsonString):
    jsonDict = json.loads(jsonString)
    validate(jsonDict, schema)
    return jsonDict

def createBooleanField(params):
    if 'default' in params:
        field = forms.BooleanField(required=False, initial=params['default'])
    else:
        field = forms.BooleanField(required=False)
    return field

def createTextField(params):
    if 'default' in params:
        field = forms.CharField(required=params['required'], initial=params['default'])
    else:
        field = forms.CharField(required=params['required'])
    return field

def createChoiceField(params):
    cs = [(c, c) for c in params['choices']]
    if 'default' in params:
        field = forms.ChoiceField(choices=cs, required=params['required'], initial=params['default'])
    else:
        field = forms.ChoiceField(choices=cs, required=params['required'])
    return field

def createDateField(params):
    if 'default' in params:
        field = forms.CharField(required=params['required'], initial=params['default'])
    else:
        field = forms.CharField(required=params['required'])
    return field

def createTimeField(params):
    if 'default' in params:
        field = forms.CharField(required=params['required'], initial=params['default'])
    else:
        field = forms.CharField(required=params['required'])
    return field

def createDecimalField(params):
    if 'default' in params:
        field = forms.DecimalField(required=params['required'], initial=params['default'])
    else:
        field = forms.DecimalField(required=params['required'])
    return field

def convertJsonToForm(jsonString):
    schema = getSchemaFromFile(FORM_SCHEMA_FILE)
    jsonDict = validateFromString(schema, jsonString)

    fieldFuncs = {
        "boolean": createBooleanField,
        "text": createTextField,
        "choice": createChoiceField,
        "date": createDateField,
        "time": createTimeField,
        "number": createDecimalField
    }

    form = AppSettingsForm()
    del form.fields['placeholder']

    for field in jsonDict['fields']:
        form.fields[field['name']] = fieldFuncs[field['type']](field)

    return form