from django.contrib import admin
from django.utils.safestring import mark_safe
from django import forms

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Person, Genre, Category, Movie, MovieShots, RatingStars, Rating, Review, Country


class MovieAdminForm(forms.ModelForm):
    description = forms.CharField(label="Описание", widget=CKEditorUploadingWidget())

    class Meta:
        model = Movie
        fields = "__all__"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "url")
    list_display_links = ("name", "id")


class ReviewsInline(admin.TabularInline):
    model = Review
    extra = 1
    readonly_fields = ("name", "email")


class MovieShotsInline(admin.TabularInline):
    model = MovieShots
    extra = 1
    readonly_fields = ("get_image", )

    def get_image(self, obj):
        return mark_safe(f"<img src={obj.image.url} width='100' height='110'>")

    get_image.short_description = "Изображение"


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "get_image", "category", "year", "draft")
    list_display_links = ("title", "id")
    list_filter = ("category", "year")
    search_fields = ("title", "category__name", "year")
    actions = ["publish", "unpublish"]
    inlines = [MovieShotsInline, ReviewsInline]
    save_on_top = True
    save_as = True
    list_editable = ("draft",)
    form = MovieAdminForm
    readonly_fields = ("get_image", )
    fieldsets = (
        (None, {
           "fields": (("title", "tagline"), )
        }),
        (None, {
            "fields": (("genres", "category", "countries"),)
        }),
        (None, {
            "fields": ("description", ("poster", "get_image"), )
        }),
        (None, {
            "fields": (("year", "world_premier"), )
        }),
        (None, {
            "fields": (("budget", "fees_in_usa", "fees_in_world"), )
        }),
        ("Persons", {
            "classes": ("collapse", ),
            "fields": (("directors", "actors"), )
        }),
        ("Options", {
            "fields": (("slug", "draft"),)
        }),
    )

    def get_image(self, obj):
        return mark_safe(f"<img src={obj.poster.url} width='50' height='60'>")

    def unpublish(self, request, queryset):
        """Снять с публикации"""
        row_update = queryset.update(draft=True)
        if row_update == 1:
            message = "1 запись обновлена"
        else:
            message = f"{row_update} записей обновлены"
        self.message_user(request, f"{message}")

    def publish(self, request, queryset):
        """Снять с публикации"""
        row_update = queryset.update(draft=False)
        if row_update == 1:
            message = "1 запись обновлена"
        else:
            message = f"{row_update} записей обновлены"
        self.message_user(request, f"{message}")

    unpublish.short_description = "Снять с публикации"
    unpublish.allowed_permissions = ("change", )

    publish.short_description = "Опубликовать"
    publish.allowed_permissions = ("change", )

    get_image.short_description = "Постер"


@admin.register(Review)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "parent", "movie")
    list_display_links = ("name", "email", "id")
    list_filter = ("movie", "email", "parent")
    search_fields = ("name", "email", "movie")
    readonly_fields = ("name", "email")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "second_name", "get_age", "get_image")
    list_display_links = ("last_name", "first_name", "id")
    search_fields = ("first_name", "last_name", "second_name")
    readonly_fields = ("get_image", )

    def get_image(self, obj):
        return mark_safe(f"<img src={obj.image.url} width='50' height='60'>")

    get_image.short_description = "Изображение"


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "url")
    list_display_links = ("name", "id")
    search_fields = ("name", )


@admin.register(MovieShots)
class MovieShotsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "movie", )
    list_display_links = ("title", "id")
    list_filter = ("movie__title", )
    search_fields = ("title", "movie")


@admin.register(RatingStars)
class RatingStarsAdmin(admin.ModelAdmin):
    pass


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "ip", "movie", "star")
    list_display_links = ("ip", "id")
    list_filter = ("movie", "ip", "star")
    search_fields = ("ip", "email")
    readonly_fields = ("ip", "movie", "star")


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


admin.site.site_title = "Django Movies"
admin.site.site_header = "Django Movies"
