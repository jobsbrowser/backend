from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=64, db_index=True)

    def __str__(self):
        return self.name


class Offer(models.Model):
    url = models.URLField()
    offer_id = models.CharField(max_length=16)
    date_posted = models.DateField(db_index=True)
    valid_through = models.DateField(db_index=True)

    job_title = models.CharField(max_length=256)
    job_location = models.CharField(max_length=512)
    employer = models.CharField(max_length=256)

    raw_html = models.TextField()
    job_description = models.TextField()
    job_benefits = models.TextField()
    job_qualifications = models.TextField()

    tags = models.ManyToManyField('Tag', through='TagOfferRelationship')

    def __str__(self):
        return f"[{self.offer_id}] {self.job_title}"

    class Meta:
        ordering = ['-valid_through']


class TagOfferRelationship(models.Model):
    tag = models.ForeignKey('Tag')
    offer = models.ForeignKey('Offer')
    priority = models.FloatField(default=1)
