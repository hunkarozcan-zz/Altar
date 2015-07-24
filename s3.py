import boto.sqs
import app_settings
import image
import tempfile
import logging
import cloudwatch

class s3(object):
    """Manages s3 operations like download, upload, backup etc."""

    cw=cloudwatch.Cloudwatch()
    def __init__(self):
        conf=app_settings.Config()
        self.conn = boto.connect_s3()
        
            
    def download(self, im):
        
        # set tempfile suffix to .png whether file is png or not because of PngOptimizerCL's weird suffix check. :/
        im.tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        b=self.conn.get_bucket(im.source_bucket)
        key=b.get_key("/"+im.source_path)
        im.acl=key.get_acl()
        im.metadatas=key.metadata

        if len(im.headers) == 0: 
            # if there are no http headers set by user, set them from source
            im.headers['Cache-Control']=key.cache_control
            im.headers['Content-Type']=key.content_type
            im.headers['Content-Encoding']=key.content_encoding
            im.headers['Content-Disposition']=key.content_disposition
            im.headers['Content-Language']=key.content_language
            im.headers['Etag']=key.etag
      
        
        if key is None:
            logging.error("File not found!")
            return False
        else:
            key.get_contents_to_file(im.tf)
            im.size = im.tf.tell()
            im.tf.seek(0)
            logging.info("Image downloaded:%s - %s",im.size,im.tf.name)
            self.cw.send_download(im.size)
            im.tempFilePath=im.tf.name
            im.tf.close()
            print(im.tf.name)
            return True

    def upload(self,im):
        if im.backup:
            self.backupFile(im)
        logging.info('Starting Upload...')

        b=self.conn.get_bucket(im.destination_bucket)
        key=b.new_key("/"+im.destination_path)
        
        # set all custom metadata
        for mtd in im.metadatas:
            key.set_metadata(mtd,im.metadatas[mtd])       

        key.set_contents_from_file(open(im.tempFilePath,'rb'),im.headers)
        
        # Set ACL information from source to new file
        key.set_acl(im.acl)

        self.cw.send_upload(im.optimized_size)
        logging.info("Upload Complete %s",key)

    def backupFile(self,im):
        backupDir=im.replace_last(im.destination_path,"/","/backup/")
        logging.info("Need Backup, Backing Up to <%s>",backupDir)
        b=self.conn.get_bucket(im.destination_bucket)
        key=b.copy_key(backupDir,im.source_bucket,im.source_path)
        logging.info("Copied %s",key)
