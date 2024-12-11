from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateTimeLocalField
from wtforms.validators import DataRequired, Optional

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    start_datetime = DateTimeLocalField('Start Date & Time', 
                                      format='%Y-%m-%dT%H:%M',
                                      validators=[DataRequired()])
    end_datetime = DateTimeLocalField('End Date & Time', 
                                    format='%Y-%m-%dT%H:%M',
                                    validators=[DataRequired()])
    location_name = StringField('Location Name', validators=[Optional()])
    street_name = StringField('Street Name', validators=[Optional()])
    street_number = StringField('Street Number', validators=[Optional()])
    postal_code = StringField('Postal Code', validators=[Optional()])
    file = FileField('Upload File', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Only images and PDF files are allowed!')
    ])