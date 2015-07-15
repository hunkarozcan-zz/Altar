import boto.sqs
import app_settings
import json
import logging


class Sqs:
    def __init__(self):
        
        conf=app_settings.Config()
        conn = boto.sqs.connect_to_region(conf.region)
        
        self.q = conn.get_queue(conf.sqsName)
        if self.q==None:
            raise

    def getMessage(self,count):
        msgs = self.q.get_messages(count,wait_time_seconds=2)
        logging.info("Got %s message(s)" % len(msgs))
        return msgs
        
    
