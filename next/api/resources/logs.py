"""
next_backend Logs Resource
author: Christopher Fernandez, Lalit Jain
Logs resource for all logs associated with a specified experiment.
"""

'''
example use:
get a tripletMDS query:
curl -X GET http://localhost:8001/api/experiment/[exp_uid]/logs
'''


from flask import Flask, request, send_file
from flask_restful import Resource, reqparse
import json
import zipfile
from io import BytesIO as BytesIO
import next.utils
from next.api.api_util import *
from next.api.api_util import APIArgument
from next.api.resource_manager import ResourceManager
resource_manager = ResourceManager()

# Request parser. Checks that necessary dictionary keys are available in a given resource.
# We rely on learningLib functions to ensure that all necessary arguments are available and parsed.
post_parser = reqparse.RequestParser(argument_class=APIArgument)

# Custom errors for GET and POST verbs on experiment resource
meta_error = {
    'ExpDoesNotExistError': {
        'message': "No experiment with the specified experiment ID exists.",
        'code': 400,
        'status': 'FAIL'
    },
}

meta_success = {
    'code': 200,
    'status': 'OK'
}

# Logs resource class


class Logs(Resource):

    def get(self, exp_uid, log_type=None):
        """
        .. http:get:: /experiment/<exp_uid>/logs/<log_type>

        Get all logs associated with a given exp_uid.

        **Example request**:

        .. sourcecode:: http

        GET /experiment/<exp_uid>/logs/APP-EXCEPTION HTTP/1.1
        Host: next_backend.next.discovery.wisc.edu

        **Example response**:

        .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        [
            log_data: [experiment_logs],
            status: {
                code: 200,
                status: OK,
            },
        ]

        :>json log_data: list experiment_logs of all logs for specified experiment.

        :statuscode 200: Logs successfully returned
        :statuscode 400: Logs failed to be generated
        """

        zip_true = False
        if request.args.get('zip'):
            try:
                zip_true = eval(request.args.get('zip'))
            except:
                pass

        # Get logs for exp_uid from resource_manager
        if log_type:
            experiment_logs = resource_manager.get_experiment_logs_of_type(exp_uid,
                                                                           log_type)
            all_logs = {'log_data': experiment_logs}
            return attach_meta(all_logs, meta_success), 200
        else:
            experiment_logs = resource_manager.get_experiment_logs(exp_uid)
            all_logs = {'log_data': experiment_logs}
            if zip_true:
                zip_logs = BytesIO()
                with zipfile.ZipFile(zip_logs, 'w') as zf:
                    zf.writestr('logs.json', json.dumps(all_logs))
                zip_logs.seek(0)
                return send_file(zip_logs,
                                 download_name='logs.zip',
                                 as_attachment='True')
            else:
                return attach_meta(all_logs, meta_success), 200

        if not experiment_logs:
            return attach_meta({'message': 'No logs to report.'}, meta_success), 200
