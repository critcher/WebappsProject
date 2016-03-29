from jsonschema import validate, ValidationError
import json

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