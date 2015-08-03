import app_settings
import sqs
import image
import logging
import cloudwatch
import s3
import signal
import sns

def signal_handler(signal, frame):
    print("\nEt tu, Brute?")
    exit()

conf=app_settings.Config()
qu=sqs.Sqs()
cw=cloudwatch.Cloudwatch()
as3=s3.S3()
notification=sns.Sns()

logging.basicConfig(
    filename='altar.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logging.info('Altar Started')

signal.signal(signal.SIGINT, signal_handler)

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
                        cw.send_ok()
                        notification.publish("Optimized:{}".format(img.id),"Image is optimized to %{:.2f} of it's original size\n\n\n{}".format(img.percentage,img.message.replace('", ','",\n')))
                    else:
                        logging.warning("No need to Upload")

                    msg.delete()
                except Exception as e: 
                    #TODO: Do something meaningful with this
                    logging.error("Error:{}".format(e))
                    cw.send_error()
                    #raise
            else:
                logging.error("Couldn't download File")
    except(KeyboardInterrupt, SystemExit):
        logging.info('Altar terminated by user')
        raise
    except:
        logging.error("Couldn't get messages")
        raise

logging.info('Altar Ended')
