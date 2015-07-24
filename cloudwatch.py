import boto.ec2.cloudwatch as cw
import app_settings
import logging
class Cloudwatch(object):
    """Class to Send custom metrics to CloudWatch"""

    
    
    def __init__(self):
        
        self.conf=app_settings.Config()
        self.conn = cw.connect_to_region(self.conf.region)
       

    def __send_metric(self, name, unit, value):
        try:
            self.conn.put_metric_data(namespace=self.conf.aws_cw_namespace, name=name, unit=unit, value=value)
        except:
            logging.error("Can't send metric to CloudWatch");
   
    def send_upload(self,size):
        """
        Send Uploaded file size in bytes
        Metric Name: Uploaded Data
        """
        self.__send_metric(name="Uploaded Data",unit="Bytes",value=size)

    def send_download(self,size):
        """
        Send Downloaded file size info in bytes
        Metric Name: Downloaded Data
        """
        self.__send_metric(name="Downloaded Data",unit="Bytes",value=size)

    def send_error(self):
        """
        Send Error to Cloudwatch
        Metric Name: Error Count
        """
        self.__send_metric(name="Error Count",unit="Count",value="1.0")
        
    def send_ok(self):
        """
        Send Success to Cloudwatch
        Metric Name: Optimized Count
        """
        self.__send_metric(name="Optimized Count",unit="Count",value="1.0")

    def send_saving(self,size):
        """
        Send Success to Cloudwatch
        Metric Name: Optimized Count
        """
        self.__send_metric(name="Savings",unit="Kilobytes",value=size/1024)              

