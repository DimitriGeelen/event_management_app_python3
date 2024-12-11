from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateTimeLocalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Save Category')

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
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    file = FileField('Upload File', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Only images and PDF files are allowed!')
    ])