import boto.sqs
import app_settings
import json
import logging


class Sqs:
    def __init__(self):
        
        conf=app_settings.Config()
        
        conn = boto.sqs.connect_to_region(
        conf.region,
        aws_access_key_id       = conf.aws_access_key_id,
        aws_secret_access_key   = conf.aws_secret_access_key
        )
        
        self.q = conn.get_queue(conf.sqsName)

    def getMessage(self,count):
        msgs = self.q.get_messages(count)
        logging.info("Got %s message(s)" % len(msgs))
        return msgs
        
    
