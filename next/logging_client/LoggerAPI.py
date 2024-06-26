"""
API for logging to a log database.
Kept for backwards-compatibility.
"""

import next.constants as constants
import next.utils as utils
import datetime
from next.database_client.DatabaseAPI import DatabaseAPI


class LoggerAPI(DatabaseAPI):
    def __init__(self, mongo_host=constants.MONGODB_HOST, mongo_port=constants.MONGODB_PORT,
                 database_name=constants.logs_database_id):
        super(LoggerAPI, self).__init__(mongo_host, mongo_port, database_name)

    def _normalize_logentry(self, log):
        if log.get('timestamp') and isinstance(log.get('timestamp'), datetime.datetime):
            log['timestamp'] = str(log['timestamp'])

        return log

    def log(self, bucket_id, log_dict):
        """
        Saves log_dict to PermStore as an individual document for later recall. 

        Inputs: 
            (string) bucket_id, (dict with string values) log_dict
        """
        self.set_doc(bucket_id, None, log_dict)

    def get_logs_with_filter(self, bucket_id, pattern_dict):
        """
        Retrieves all logs in bucket_id that match (i.e. contain) pattern_dict

        Inputs: 
            (string) bucket_id, (dict of string values) pattern_dict
        """
        return [self._normalize_logentry(d)
                for d in self.get_docs_with_filter(bucket_id, pattern_dict)]

    def delete_logs_with_filter(self, bucket_id, pattern_dict):
        """
        Deletes all logs in bucket_id that match (i.e. contain) pattern_dict

        Inputs: 
            (string) bucket_id, (dict of string values) pattern_dict
        """
        self.delete_docs_with_filter(bucket_id, pattern_dict)
