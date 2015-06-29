import os
class Config():
    def __init__(self):
        self.author="Hünkar Özcan"
        self.date="28.06.2015"

        # AWS Settings
        self.region="eu-west-1"
        self.sqsName="ino_altar"
        self.aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', "Default_key")
        self.aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', "Default_Secret")
        

    



