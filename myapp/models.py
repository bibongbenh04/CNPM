from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.html import format_html
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# from tinymce.models import HTMLField

User = get_user_model()

class Feature(models.Model):
	name = models.CharField(max_length=100)
	details = models.CharField(max_length=500)

class categoryQuiz(models.Model): 
    TYPE_CATEGORY_QUIZ = [
        ('TEST ONL', 'TEST ONL'),
        ('CONTEST', 'CONTEST'),
    ]
    typeCate = models.CharField(max_length=10, choices=TYPE_CATEGORY_QUIZ, default = 'TEST ONL')
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='category/')
    cat_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    url = models.CharField(max_length=100, unique=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)

    
    def image_tag(self):
        return format_html('<img src="/media/{}" style = "width:40px;height:40px;border-radius:50%" />'.format(self.image))
        
    def __str__(self):
        return self.title   

class quizQuestion(models.Model):
    is_active = models.BooleanField(default=True)
    cat = models.ForeignKey(categoryQuiz, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    choice1 = models.CharField(max_length=200)
    choice2 = models.CharField(max_length=200)
    choice3 = models.CharField(max_length=200)
    choice4 = models.CharField(max_length=200)
    correct_choice = models.IntegerField(choices=[(1, 'Choice 1'), (2, 'Choice 2'), (3, 'Choice 3'), (4, 'Choice 4')])

    def __str__(self):
        return self.question_text

#Category model
class Category(models.Model):
    is_active = models.BooleanField(default=True)
    cat_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    url = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='category/')
    add_date = models.DateTimeField(auto_now_add=True, null=True)

    def image_tag(self):
        return format_html('<img src="/media/{}" style = "width:40px;height:40px;border-radius:50%" />'.format(self.image))
    
    def __str__(self):
        return self.title   

class Post(models.Model):
    is_active = models.BooleanField(default=True)
    author = models.CharField(max_length=30)
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    # content = HTMLField()
    content = models.TextField()
    preview_content = models.CharField(max_length=1000, blank=False)
    url = models.CharField(max_length=100, unique=True)
    cat = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post/')
    add_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    name = models.CharField(max_length=225)
    body = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=None, null=True)
    object_id = models.PositiveIntegerField(default=None, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.name} - {self.date}"

class Science(models.Model):
    is_active = models.BooleanField(default=True)
    author = models.CharField(max_length=30)
    science_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    preview_content = models.CharField(max_length=1000, blank=False)
    url = models.CharField(max_length=100, unique=True)
    cat = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post/')
    add_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title
    
class Community(models.Model):
    TYPE_CHOICES = [
        ('Khác', 'Khác'),
        ('Góp Ý', 'Góp Ý'),
        ('Chia Sẽ', 'Chia Sẽ'),
        ('Kiến Thức', 'Kiến Thức'),
    ]
    is_active = models.BooleanField(default=True)
    author = models.CharField(max_length=30)
    community_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    url = models.CharField(max_length=100, unique=True)
    cat = models.CharField(max_length=100, choices = TYPE_CHOICES)
    image = models.ImageField(upload_to='post/')
    add_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

class Store(models.Model):
    is_active = models.BooleanField(default=True)
    seller = models.CharField(max_length=30)
    store_id = models.AutoField(primary_key=True)
    nameStore = models.CharField(max_length=200)
    numberStore = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    content = models.TextField()
    preview_content = models.CharField(max_length=1000, blank=False)
    numberPhone_seller = models.DecimalField(max_digits=10, decimal_places=0, default=0000000000)
    link_conection_seller = models.CharField(max_length=100)
    price_000vnd = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.CharField(max_length=100, unique=True)
    cat = models.ForeignKey(Category, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to='store/', default=None, blank=False)
    add_date = models.DateTimeField(auto_now_add=True, null=True)

    def image_tag(self):
        return format_html('<img src="/media/{}" style = "width:auto;height:100px;border-radius:40%;filter: drop-shadow(1px 1px 20px green)" />'.format(self.image))

    def __str__(self):
        return self.nameStore

class ProductImage(models.Model):
    product = models.ForeignKey(Store, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/')
    preview_content = models.CharField(max_length=1000, default="None", blank=False)

    def __str__(self):
        return f"Image for {self.product.nameStore}"

class Header(models.Model):
    is_active = models.BooleanField(default=True)
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    # logo = models.ImageField(upload_to='header_logos/'

    def __str__(self):
        return self.title

class Portfolio(models.Model):
    is_active = models.BooleanField(default=True)
    TYPE_CHOICES = [
        ('Card', 'Card'),
        ('App', 'App'),
        ('Web', 'Web'),
    ]
    typeP = models.CharField(max_length=4, choices=TYPE_CHOICES)
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    # logo = models.ImageField(upload_to='header_logos/'

    def __str__(self):
        return self.title

    

    

    
