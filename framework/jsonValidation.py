from jsonschema import validate, ValidationError
import json


def getSchemaFromFile(filename):
	""" Throws IOError if the file is invalid, and ValueError
	if the json is invalid.
	"""
    with open(filename, 'r') as f:
        schemaText = f.read()
        schemaDict = json.loads(schemaText)
    return schemaDict


def validateFromString(schema, jsonString):
	""" Throws ValueError if the json is invalid, and
    ValidationError if the json does not fit the schema.
	"""
    jsonDict = json.loads(jsonString)
    validate(jsonDict, schema)
    return jsonDict