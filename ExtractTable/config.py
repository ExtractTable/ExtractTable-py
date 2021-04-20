"""
Configure all Server request/response objects here
"""


class HOST:
    """API Endpoints of ExtractTable.com"""
    VALIDATOR = 'validator.extracttable.com'
    TRIGGER = 'trigger.extracttable.com'
    RESULT = 'getresult.extracttable.com'
    BIGFILE = 'bigfile.extracttable.com'
    TRANSACTIONS = 'viewtransactions.extracttable.com'


class JobStatus:
    """Job Status responses recieved from Server. Declared here to maintain consistency"""
    SUCCESS = 'Success'
    FAILED = 'Failed'
    PROCESSING = 'Processing'
    INCOMPLETE = 'Incomplete'
