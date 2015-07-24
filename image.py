import json
import boto.s3
import boto.s3.connection
import app_settings
import tempfile
import logging
import subprocess
import os
import imghdr
import cloudwatch


class image():
    id=""
    name=""
    source_bucket=""
    source_path=""
    destination_bucket=""
    destination_path=""
    overwrite=False
    backup=True
    size=0
    optimized_size=0
    ratio=0
    percentage=0
    type=""
    tempFilePath=""
    target_quality=80;
    conf=app_settings.Config()
    cw=cloudwatch.Cloudwatch()
    acl=None
    # Custom Metadata
    metadatas={}
    # Http Headers
    headers={}


    def __init__(self,json_data):
        j=json.loads(json_data)
        logging.info("Image Initializing from data:%s",j)
        self.source_bucket=j["source_bucket"]
        self.source_path=j["source_path"]
        self.overwrite=j.get("overwrite",False)
        self.backup=j.get("backup",True)
        self.target_quality=j.get("target_quality",80)
        self.headers=j.get("headers",{})

        if self.overwrite:
            logging.info("Set to Overwrite!")
            self.destination_bucket=self.source_bucket
            self.destination_path=self.source_path
        else:
            self.destination_bucket=j.get("destination_bucket","")
            self.destination_path=j.get("destination_path","")

 
    #TODO: Move to helper class
    def replace_last(self, source_string, replace_what, replace_with):
        head, sep, tail = source_string.rpartition(replace_what)
        return head + replace_with + tail

    def check_results(self):
        logging.info("Checking Results")
        if self.optimized_size!=0 or self.size==0:
            self.ratio=self.optimized_size/self.size
            self.percentage=100-(self.optimized_size*100/self.size)
            
            if self.ratio<1.0:
                logging.info("Optimization is success with a rate of %{}".format(self.percentage))
                return True
            elif self.ratio==1.0:
                logging.warning("This file is already optimized. Result is equal to original ({}/{})".format(self.optimized_size,self.size))
                return False
            else:
                logging.warning("Optimization is a failure. Result is larger than original ({}/{}):( ".format(self.optimized_size,self.size))
                return False
        else:
            logging.error("Optimization failed. Result too good to be true o_O Size is 0 :( File is missing I guess")
            return False

    def optimize(self):
        try:
            img_type=self.get_image_type()
            if img_type=='png':
	            # It's a png, optipng is the way!
                # f=subprocess.check_output(['optipng', self.tf.name, '-o 2'])
                
                f=subprocess.check_output(['PngOptimizerCL', '-file:"'+self.tf.name+'"'])
            elif img_type=='jpeg':
	            # "jpg is the file, use jpegoptim you must" -Yoda
                f=subprocess.check_output(['jpegoptim',self.tf.name,'-m'+self.target_quality])
            else:
                logging.error("Unsupported file type: {}".format(img_type))
                raise ValueError('Unsupported file type: {}'.format(img_type))
        except Exception as e:
            logging.error(e)

        logging.info("Optimization result:"+f.decode("utf-8"))
        self.optimized_size=os.path.getsize(self.tf.name)
        logging.info("Result file size:{}".format(self.optimized_size))
        
    def get_image_type(self):
        self.type=imghdr.what(self.tf.name)
        logging.info("Image type {}: ".format(self.type))
        return self.type
