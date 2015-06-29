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



messages=qu.getMessage(1)


for msg in messages:
    #print("Message Body:",msg.get_body())
    img=image.image(msg.get_body())
    
    #print("image:",img.source_path)
    
    #qu.getAltarProperties(msg)
    #print("Serialized:",qu.getAltarProperties(msg))
    
    img.downloadFromS3()
    img.uploadToS3()


logging.info('Altar Ended')
