import sys
sys.path.append('.')
from flask import Flask, request
from flask_restful import Resource, Api
from marshmallow import Schema, fields, ValidationError

from template_compliance.template_conformance_core import check_rupp_template_compliance, check_ears_template_compliance, check_agile_story_template_conformance


class TemplateConformanceSchema(Schema):
    conformance = fields.Str(required=True)
    requirements = fields.Str(required=True)
    class Meta:
        strict = True


class RequirementConformance(Resource):

    def post(self):
        input_request = request.get_json(force=True)
        try:
            result = TemplateConformanceSchema().load(input_request)
        except ValidationError:
            return {'message': 'Invalid json request'}, 400
        else:
            #print(input_request.get('conformance'))
            if input_request.get('conformance').lower() == 'rupp':
                template = 'rupp'
            elif input_request.get('conformance').lower() == 'ears':
                template = 'ears'
            elif input_request.get('conformance').lower() == 'agile':
                template = 'agile'
            else:
                return {'message': 'Invalid option for conformance'}, 400
            requirements = input_request.get('requirements')
        #print(requirements)
        if requirements:
            if template == 'rupp':
                tagged_requirements_list = check_rupp_template_compliance(requirements)
                return tagged_requirements_list
            elif template == 'ears':
                tagged_requirements_list = check_ears_template_compliance(requirements)
                return tagged_requirements_list
            elif template == 'agile':
                tagged_requirements_list = check_agile_story_template_conformance(requirements)
                return tagged_requirements_list
        else:
            return {'message': 'Empty requirement(s)'}, 400


if __name__=='__main__':
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(RequirementConformance, '/conformance')
    app.run(host='0.0.0.0', port=5000, debug=True)