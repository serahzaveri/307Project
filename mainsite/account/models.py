from django.contrib.auth.models import User, auth
from django.db.models import Q
from django.urls import reverse
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

def upload_location(instance, filename):
	file_path = 'account/{author_id}/{title}-{filename}'.format(
				author_id=str(instance.author.id),title=str(instance.title), filename=filename)
	return file_path


class ItemPost(models.Model):
	title 					= models.CharField(max_length=50, null=False, blank=False)
	body 					= models.TextField(max_length=5000, null=False, blank=False)
	price 					= models.DecimalField(max_digits=7, null=False, decimal_places=2, default='0.00')
	inventory				= models.DecimalField(max_digits=7, null=False, decimal_places=2, default='0')
	image		 			= models.ImageField(upload_to=upload_location, null=True, blank=True)
	date_published 			= models.DateTimeField(auto_now_add=True, verbose_name="date published")
	date_updated 			= models.DateTimeField(auto_now=True, verbose_name="date updated")
	author 					= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	slug 					= models.SlugField(blank=True, unique=True)

	def get_absolute_url(self):
		return reverse('account:models', kwargs={'pk': self.pk})

	def __str__(self):
		return self.title

@receiver(post_delete, sender=ItemPost)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False) 

def pre_save_item_post_receiver(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = slugify(instance.author.username + "-" + instance.title)

pre_save.connect(pre_save_item_post_receiver, sender=ItemPost)





