from django.contrib import admin
from django import forms
from .models import quizQuestion, Category, Post, categoryQuiz, Science, Header, Portfolio, Store, Comment, Community, ProductImage
from django.core.exceptions import ValidationError
from django.db.models import Q
# Register your models here.
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Số lượng form trống hiển thị mặc định

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('image_tag','title', 'description', 'url', 'add_date')
    # list_display = ('title', 'description', 'url', 'add_date')
    search_fields = ('title',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    list_filter = ('cat',)
    list_per_page = 5

    class Media:
        js = ('https://cdn.tiny.cloud/1/3q1fzzm9ciix8rz2k5kj1v8vwyymlrhnq1a85iji04lb7i0n/tinymce/5/tinymce.min.js','assets/js/TextPost.js',)

class StoreAdmin(admin.ModelAdmin):
    list_display = ( 'nameStore',)
    search_fields = ('nameStore',)
    list_filter = ('cat',)
    list_per_page = 5
    inlines = [ProductImageInline]

    class Media:
        js = ('https://cdn.tiny.cloud/1/3q1fzzm9ciix8rz2k5kj1v8vwyymlrhnq1a85iji04lb7i0n/tinymce/5/tinymce.min.js','assets/js/TextPost.js',)

class StoreAdminForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(StoreAdminForm, self).__init__(*args, **kwargs)
        self.fields['seller'].widget.attrs['placeholder'] = 'Người Bán Sản Phẩm'
        self.fields['nameStore'].widget.attrs['placeholder'] = 'Tên Sản Phẩm'
        self.fields['numberStore'].widget.attrs['placeholder'] = 'Số Lượng Sản Phẩm'
        self.fields['preview_content'].widget.attrs['placeholder'] = 'Mô Tả Xem Trước'
        self.fields['numberPhone_seller'].widget.attrs['placeholder'] = 'Số Của Người Bán'
        self.fields['link_conection_seller'].widget.attrs['placeholder'] = 'Đường Link Liên Hệ'
        self.fields['price_000vnd'].widget.attrs['placeholder'] = 'Đơn Giá(Nghìn Đồng)'
        self.fields['url'].widget.attrs['placeholder'] = '-> store/url'

# QuizQuestion.objects.all().delete()
# admin.site.register(categoryQuiz, CategoryAdmin)
admin.site.register(quizQuestion)
# admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Science, PostAdmin)
admin.site.register(Header)
admin.site.register(Portfolio)
# admin.site.register(Store, StoreAdmin)
# admin.site.register(Store, ProductAdmin)
# admin.site.register(Community, PostAdmin)
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    form = StoreAdminForm




