import json
import boto.s3
import boto.s3.connection
import app_settings
import tempfile
import logging
import os

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
    conf=app_settings.Config()


    def __init__(self,json_data):
        j=json.loads(json_data)
        logging.info("Image Initializing from data:%s",j)
        self.source_bucket=j["source_bucket"]
        self.source_path=j["source_path"]
        self.overwrite=j.get("overwrite",False)
        self.backup=j.get("backup",True)
        print(self.overwrite)
        if self.overwrite:
            logging.info("Set to Overwrite!")
            self.destination_bucket=self.source_bucket
            self.destination_path=self.source_path
        else:
            self.destination_bucket=j.get("destination_bucket","")
            self.destination_path=j.get("destination_path","")

    def downloadFromS3(self):

        conn=self.connectToS3()

        self.tf = tempfile.NamedTemporaryFile(delete=False)

        b=conn.get_bucket(self.source_bucket)
        key=b.get_key("/"+self.source_path)
        key.get_contents_to_file(self.tf)
        self.size = self.tf.tell()
        self.tf.seek(0)
        logging.info("Image downloaded:%s",self.size)
        print(self.tf.name)

    def uploadToS3(self):
        if self.backup:
            self.backupFile()
        logging.info('Starting Upload...')
        conn=self.connectToS3()

        b=conn.get_bucket(self.destination_bucket)
        key=b.new_key("/"+self.destination_path)
        #TODO: Add metadata regarding the type of original file
        key.set_metadata('Content-Type', 'image/png')
        key.set_contents_from_file(self.tf)
        
        logging.info("Upload Complete %s",key)
        

    def connectToS3(self):
        c = boto.connect_s3(
        aws_access_key_id       = self.conf.aws_access_key_id,
        aws_secret_access_key   = self.conf.aws_secret_access_key
        )
        return c

    def replace_last(self, source_string, replace_what, replace_with):
        head, sep, tail = source_string.rpartition(replace_what)
        return head + replace_with + tail

    def backupFile(self):
        backupDir=self.replace_last(self.source_path,"/","/backup/")
        logging.info("Need Backup, Backing Up to <%s>",backupDir)
        conn=self.connectToS3()
        b=conn.get_bucket(self.destination_bucket)
        key=b.copy_key(backupDir,self.source_bucket,self.source_path)
        logging.info("Copied %s",key)


    def optimize(self):
        # It's png only for now 
        f = os.popen('optipng '+self.tf.name + " −v -o 2")
        logging.info("OptiPNG result:"+f.read())
        

        
