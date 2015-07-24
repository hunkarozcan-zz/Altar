import app_settings
import sqs
import image
import logging
import cloudwatch
import s3

conf=app_settings.Config()
qu=sqs.Sqs()
cw=cloudwatch.Cloudwatch()
as3=s3.s3()

logging.basicConfig(
    filename='altar.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logging.info('Altar Started')

while True:

    try:
        messages=qu.getMessage(1)
        for msg in messages:
            img=image.image(msg.get_body())
            if as3.download(img):
                try:
                    img.optimize()
                    if img.check_results():
                        logging.info("Optimization is a success. Uploading...")
                        as3.upload(img)
                        cw.send_metric(name="Optimized Count",unit="Count",value="1.0")
                    else:
                        logging.warning("No need to Upload")

                    msg.delete()
                except Exception as e: 
                    #TODO: Do something meaningful with this
                    logging.error("Error:{}".format(e))
                    cw.send_metric(name="Error Count",unit="Count",value="1.0")
                    #raise
            else:
                logging.error("Couldn't download File")
    except:
        logging.error("Couldn't get messages")
        raise

logging.info('Altar Ended')
