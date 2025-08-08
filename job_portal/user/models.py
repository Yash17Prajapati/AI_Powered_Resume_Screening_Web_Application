# from mongoengine import Document, StringField, FileField, ReferenceField

# class Application(Document):
#     meta = {'db_alias': 'user_db'}  # Use the user database
#     user = StringField(required=True)  # Could store the candidate's username or ID
#     job = ReferenceField('Job')  # Reference the Job model from the recruiter database
#     resume = FileField()
