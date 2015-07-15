import boto.ec2.cloudwatch as cw
import app_settings
import logging
class Cloudwatch(object):
    """description of class"""

    
    
    def __init__(self):
        
        self.conf=app_settings.Config()
        self.conn = cw.connect_to_region(self.conf.region)
       

    def send_metric(self, name, unit, value):
        try:
            self.conn.put_metric_data(namespace=self.conf.aws_cw_namespace, name=name, unit=unit, value=value)
        except:
            logging.error("Can't send metric to CloudWatch");
        

