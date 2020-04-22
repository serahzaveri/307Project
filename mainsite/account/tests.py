#Imports
import datetime
from django.test import TestCase
from django.http import HttpResponse
from account.models import ItemPost
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from account.forms import SignupForm, LoginForm, CreateItemPostForm, UpdateItemPostForm
from account.views import PostDelete
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from random import seed
from random import random, randint
import datetime

#Global Vars
seed(1)
randPrice = round(random(), 2)
randInventory = randint(0,5000)
date = timezone.now()

#models test

class BaseModelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
    	print("Running: setUpClass for BaseModelTestCase")
    	super(BaseModelTestCase, cls).setUpClass()
    	my_user = User.objects.create_user('myuser', 'myemail@test', 'password')
    	cls.item_post1 = ItemPost(title="Clothes", body="They're clothes.", price=randPrice, inventory=randInventory, image="null", date_published=date, date_updated=date, author=my_user, slug=' ')
    	cls.item_post1.save()


class ItemPostTestCase(BaseModelTestCase):
	def setUp(self):
		pass
	def tearDown(self):
		pass
	def test_title(self):
		print("Running MODELS TEST: test_title")
		self.assertEqual(self.item_post1.title, "Clothes")
	def test_body(self):
		print("Running MODELS TEST: test_body")
		self.assertEqual(self.item_post1.body, "They're clothes.")
	def test_price(self):
		print("Running MODELS TEST: test_price")
		self.assertEqual(self.item_post1.price, randPrice)
	def test_inventory(self):
		print("Running MODELS TEST: test_inventory")
		self.assertEqual(self.item_post1.inventory, randInventory)
	def test_image(self):
		print("Running MODELS TEST: test_image")
		self.assertEqual(self.item_post1.image, "null")
	def test_datepublished(self):
		print("Running MODELS TEST: test_datepublished")
		self.assertTrue(isinstance(self.item_post1.date_published, datetime.datetime))
	def test_dateupdated(self):
		print("Running MODELS TEST: test_dateupdated")
		self.assertTrue(isinstance(self.item_post1.date_updated, datetime.datetime))
	def test_author(self):
		print("Running MODELS TEST: test_author")
		self.assertTrue(isinstance(self.item_post1.author, User))
	def test_slug(self):
		print("Running MODELS TEST: test_slug")
		self.assertEqual(self.item_post1.slug, ' ')

#forms test
'''
class setUpClassForms(TestCase):
	def setUpForm(self):
		self.user = ItemPost.objects.create(title="Clothes", body="They're clothes.", price=randPrice, inventory=randInventory, image="null")
class CreateItemPostForm(TestCase):
	def test_userform(self):
		form = CreateItemPostForm({'title': "Clothes", 'body': "They're clothes.", 'price': randPrice, 'inventory': randInventory, 'image': "null"})
		self.assertTrue(form.is_valid())
'''

#views test
class ProjectTests(TestCase):
	def setUpViews(self):
		my_user = User.objects.create(username='myuser', email='myuser@test')
		my_user.set_password('password')
		my_user.save()

	def test_homepage(self):
		print("Running VIEWS TEST: test_homepage")
		response = self.client.get('/')
		self.assertEqual(response.status_code,200)
	def test_outofbounds(self):
		print("Running VIEWS TEST: test_outofbounds")
		response = self.client.get('/'+str(randint(0,10000)))
		self.assertEqual(response.status_code, 404)
	def test_info_loggedin(self):
		print("Running VIEWS TEST: test_info_loggedin")
		self.client.login(username='myuser', password='password')
		response = self.client.get(reverse('acc_info'))
		self.assertEquals(response.status_code, 200)
	def test_about(self):
		print("Running VIEWS TEST: test_about")
		response = self.client.get(reverse('about'))
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'about.html')
	def test_signup(self):
		print("Running VIEWS TEST: test_signup")
		response = self.client.get(reverse('signup'))
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'signup.html')
	def test_login(self):
		print("Running VIEWS TEST: test_login")
		response = self.client.get(reverse('login'))
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'login.html')
	def test_logout(self):
		print("Running VIEWS TEST: test_logout")
		response = self.client.get(reverse('logout'))
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, reverse('login'))
	def test_buy(self):
		print("Running VIEWS TEST: test_buy")
		response = self.client.get(reverse('buy'))
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'buy.html')
	def test_createItem_loggedout(self):
		print("Running VIEWS TEST: test_createItem_loggedout")
		response = self.client.get(reverse('create'))
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, reverse('login'))
	def test_createItem_loggedin(self):
		print("Running VIEWS TEST: test_createItem_loggedin")
		self.client.login(username='myuser', password='password')
		response = self.client.get(reverse('buy'))
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'buy.html')
	def test_homescreen(self):
		print("Running VIEWS TEST: test_homescreen")
		response = self.client.get(reverse('home2'))
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'home2.html')

	
'''
def test_noItem_detailview(self):
		createItemView = CreateItemPostForm(None, None)
		response = self.client.get(reverse('create_item_view'))
		self.assertEquals(response.context['form'], createItemView)

class PostDeleteTests(TestCase):
	def setUpPostDelete(self):

	def test_postdelete(self):
		response = PostDelete.as_view()(self)
		dummy_postdelete = self.DummyPostDelete()
		context = dummy_postdelete.test_func()
		self.assertTrue(context)

'''

	

