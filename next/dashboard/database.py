"""
next_backend Logs Resource
author: Christopher Fernandez, Lalit Jain
Logs resource for all logs associated with a specified experiment.
"""
from flask import Response, request, redirect
from flask_restful import Resource, reqparse

import subprocess
import next.utils
import next.broker.broker
import next.constants as constants
from next.api.api_util import *
from next.api.api_util import APIArgument
from next.api.resource_manager import ResourceManager
from next.database.database_lib import make_mongodump, restore_mongodump

resource_manager = ResourceManager()
broker = next.broker.broker.JobBroker()

# Request parser. Checks that necessary dictionary keys are available.
# learningLib functions ensure that all necessary arguments are available.
post_parser = reqparse.RequestParser(argument_class=APIArgument)
meta_success = {
    'code': 200,
    'status': 'OK'
}

# Logs resource class


class DatabaseBackup(Resource):
    def get(self):
        """
        .. http:get:: /databaseBackup

        Get a tar copy of the database.

        **Example request**:

        .. sourcecode:: http

        GET /databaseBackup HTTP/1.1

        **Example response**:

        .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        :statuscode 200: Database backup successfully returned
        :statuscode 400: database backup failed to be generated
        """
        exp_uid_list = request.args.getlist('exp_uid')  # returns a list
        name = '{}.{}'.format(str(next.utils.datetimeNow().strftime("%Y-%m-%d_%H:%M:%S")),
                              'tar.gz')
        location = make_mongodump(name, exp_uid_list)
        zip_file = file(location)
        return Response(zip_file,
                        mimetype='application/octet-stream',
                        headers={'Content-Disposition':
                                 'attachment;filename={}'.format(name)})


class DatabaseRestore(Resource):
    def post(self):
        """
        .. http:get:: /databaseBackup

            Get a tar copy of the database.

        **Example request**:

        .. selfourcecode:: http

            GET /databaseBackup HTTP/1.1

            **Example response**:

            .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        :statuscode 200: Database backup successfully returned
        :statuscode 400: database backup failed to be generated
        """
        zip_file = request.files['primary_file']
        # zip_file is a file object
        subprocess.call('mkdir -p /dump', shell=True)
        filename = '/dump/mongo_dump_restore.tar.gz'
        zip_file.save(filename)
        restore_mongodump(filename)
        subprocess.call('rm '+filename, shell=True)

        if constants.SITE_KEY:
            dashboard_prefix = '/dashboard/{}'.format(constants.SITE_KEY)
        else:
            dashboard_prefix = '/dashboard'
        return redirect(dashboard_prefix + '/experiment_list')
