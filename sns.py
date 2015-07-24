import app_settings
import boto.sns
import logging

class sns(object):
    """Handles Simple Notification Service operations for Altar"""

    
    def __init__(self):
        self.conf=app_settings.Config()
        self.conn = boto.sns.connect_to_region(self.conf.region)
        
    def publish(self,subject,message):
        try:
            self.conn.publish(self.conf.aws_sns_topic_arn,message,subject=subject)
        except Exception as e:
            logging.error("SNS Error")



