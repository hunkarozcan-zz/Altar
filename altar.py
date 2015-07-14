import app_settings
import sqs
import image
import logging

conf=app_settings.Config()
qu=sqs.Sqs()
logging.basicConfig(
    filename='altar.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logging.info('Altar Started')

#while True:

messages=qu.getMessage(1)

for msg in messages:
    img=image.image(msg.get_body())
    if img.downloadFromS3():
        try:
            img.optimize()
            img.uploadToS3()
            msg.delete()
        except:
            #TODO: Do something meaningful with this
            logging.error("Error")
            raise

logging.info('Altar Ended')
