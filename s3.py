import boto.sqs
import app_settings
import image
import tempfile
import logging

class s3(object):
    """Manages s3 operations like download, upload, backup etc."""

    def __init__(self):
        conf=app_settings.Config()
        self.conn = boto.connect_s3()

            
    def download(self, im):
        
        # set tempfile suffix to .png whether file is png or not because of PngOptimizerCL's weird suffix check. :/
        im.tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        b=self.conn.get_bucket(im.source_bucket)
        key=b.get_key("/"+im.source_path)
        
        if key is None:
            logging.error("File not found!")
            return False
        else:
            key.get_contents_to_file(im.tf)
            im.size = im.tf.tell()
            im.tf.seek(0)
            logging.info("Image downloaded:%s - %s",im.size,im.tf.name)
            im.tempFilePath=im.tf.name
            im.tf.close()
            print(im.tf.name)
            im.cw.send_metric(name="Downloaded Data",unit="Bytes",value=im.size)
            return True

    def upload(self,im):
        if im.backup:
            self.backupFile(im)
        logging.info('Starting Upload...')

        b=self.conn.get_bucket(im.destination_bucket)
        key=b.new_key("/"+im.destination_path)
        
        if im.type=="png":
            key.set_metadata('Content-Type', 'image/png')
        elif im.type=="jpeg":
            key.set_metadata('Content-Type', 'image/jpeg')
       
        key.set_contents_from_file(open(im.tempFilePath,'rb'))
        im.cw.send_metric(name="Uploaded Data",unit="Bytes",value=im.optimized_size)
        logging.info("Upload Complete %s",key)

    def backupFile(self,im):
        backupDir=im.replace_last(im.destination_path,"/","/backup/")
        logging.info("Need Backup, Backing Up to <%s>",backupDir)
        b=self.conn.get_bucket(im.destination_bucket)
        key=b.copy_key(backupDir,im.source_bucket,im.source_path)
        logging.info("Copied %s",key)
