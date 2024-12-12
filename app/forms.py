from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeLocalField, SelectField, FileField
from wtforms.validators import DataRequired, Optional, Length
from datetime import datetime

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=200)])

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    start_datetime = DateTimeLocalField('Start Date & Time',
                                      format='%Y-%m-%dT%H:%M',
                                      validators=[DataRequired()],
                                      default=datetime.now)
    end_datetime = DateTimeLocalField('End Date & Time',
                                    format='%Y-%m-%dT%H:%M',
                                    validators=[DataRequired()],
                                    default=datetime.now)
    location_name = StringField('Location Name', validators=[Optional(), Length(max=100)])
    street_name = StringField('Street Name', validators=[Optional(), Length(max=100)])
    street_number = StringField('Street Number', validators=[Optional(), Length(max=20)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    category_id = SelectField('Category', coerce=int)
    file = FileField('File (PDF or Image)', validators=[Optional()])
