from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import secrets
class ShortURL(models.Model):


    def clean(self):
        val = URLValidator()
        try:
            val(self.long_url)
        except ValidationError:
            raise ValidationError({"long_url": "Enter a valid URL."})

    short_code = models.CharField(max_length=30, unique=True, db_index=True)
    long_url = models.TextField()
    delete_token = models.CharField(max_length=64, default=secrets.token_hex)
    click_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.short_code
