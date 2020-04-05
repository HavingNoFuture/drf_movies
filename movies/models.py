from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.db.models.signals import post_save

from datetime import date

from transliterate import translit


def get_client_ip(request):
    """Возвращает ip пользователя через запрос"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Models

class Country(models.Model):
    name = models.CharField("Имя", max_length=90)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"


class Person(models.Model):
    """Актеры и режиссеры"""
    first_name = models.CharField("Имя", max_length=90)
    last_name = models.CharField("Фамилия", max_length=90)
    second_name = models.CharField("Отчество", max_length=90, blank=True)
    countries = models.ManyToManyField(Country, verbose_name="страны", related_name="person_country")
    date_of_birthday = models.DateField("Дата рождния")
    date_of_death = models.DateField("Дата смерти", blank=True, null=True, default=None)
    description = models.TextField("Описание")
    image = models.ImageField("Изображение", upload_to="actors/")
    slug = models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        """
        Пытаемся создать слаг-транслит русских имени и фамилии, иначе делает слаг из английского.
        Обязательные требования: у модели должны быть поля first_name, last_name и slug.
        Пример: Арнольд Шварцнеггер(id:1) -> 1-arnold-shvartsnegger
        """
        if not self.slug:
            try:
                self.slug = f"{self.pk}-" \
                    f"{slugify(translit(f'{self.first_name} {self.last_name}', reversed=True))}"
            except:
                self.slug = f"{self.pk}-{slugify(f'{self.first_name} {self.last_name}')}"
            self.save(update_fields=("slug",))

    def get_age(self):
        if self.date_of_death:
            return (self.date_of_death - self.date_of_birthday).days // 365
        else:
            return (date.today() - self.date_of_birthday).days // 365

    def get_full_name(self):
        full_name = f"{self.first_name} {self.second_name} {self.last_name}" if self.second_name else \
            f"{self.first_name} {self.last_name}"
        return full_name

    def get_absolute_url(self):
        return reverse('person_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = "Актеры и режиссеры"
        verbose_name_plural = "Актеры и режиссеры"


class Genre(models.Model):
    """Жанры"""
    name = models.CharField("Жанр", max_length=60)
    description = models.TextField("Описание")
    url = models.SlugField(max_length=60, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Category(models.Model):
    """Категории"""
    name = models.CharField("Категория", max_length=150)
    description = models.TextField("Описание")
    url = models.SlugField(max_length=150, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        pass

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Movie(models.Model):
    """Фильмы"""
    title = models.CharField("Название", max_length=120)
    tagline = models.CharField("Слоган", max_length=120, default="")
    description = models.TextField("Описание")
    poster = models.ImageField("Постер", upload_to="movies/")
    year = models.PositiveIntegerField("Дата выхода", default=2019)
    countries = models.ManyToManyField(Country, verbose_name="страны", related_name="movie_country", blank=True)
    directors = models.ManyToManyField(Person, verbose_name="режиссеры", related_name="movie_director")
    actors = models.ManyToManyField(Person, verbose_name="актеры", related_name="movie_actor")
    genres = models.ManyToManyField(Genre, verbose_name="жанры")
    world_premier = models.DateField("Премьера в мире", default=date.today)
    budget = models.PositiveIntegerField("Бюджет", default=0, help_text="указывать сумму в долларах")
    fees_in_usa = models.PositiveIntegerField(
        "Сборы в США", default=0, help_text="указывать сумму в долларах"
    )
    fees_in_world = models.PositiveIntegerField(
        "Сборы в мире", default=0, help_text="указывать сумму в долларах"
    )
    category = models.ForeignKey(
        Category, verbose_name="Категория", on_delete=models.SET_NULL, null=True
    )
    draft = models.BooleanField("Черновик", default=False)
    slug = models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        """
        Пытаемся создать слаг-транслит русского названия, иначе делать слаг из английского.
        Обязательные требования: у модели должны быть поля title и slug.
        Примеры: Терминатор(id:1) -> 1-terminator
        Terminator 2(id:2) -> 2-terminator
        """
        if not self.slug:
            try:
                self.slug = f"{self.pk}-{slugify(translit(self.title, reversed=True))}"
            except:
                self.slug = f"{self.pk}-{slugify(self.title)}"
            self.save(update_fields=("slug",))

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('movie_detail', kwargs={'slug': self.slug})

    def get_reviews(self):
        return self.reviews_set.filter(parent__isnull=True)

    def get_average_rating(self):
        """Возвразает среднее значение рейтинга для фильма"""
        avg = self.rating_set.select_related().aggregate(models.Avg('star__value'))['star__value__avg']
        return avg

    def get_avg_rating_str(self):
        return "{0:.2f}".format(float(self.get_average_rating()))

    def get_current_user_rating(self, request):
        return self.rating_set.get(ip=get_client_ip(request))

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"


class MovieShots(models.Model):
    """Кадры из фильма"""
    title = models.CharField("Заголовок", max_length=120)
    description = models.TextField("Описание")
    image = models.ImageField("Изображение", upload_to="movie_shots/")
    movie = models.ForeignKey(Movie, verbose_name="Фильм", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Кадр из фильма"
        verbose_name_plural = "Кадры из фильма"


class RatingStars(models.Model):
    """Звезды рейтинга"""
    value = models.PositiveSmallIntegerField("Значение", default=0)

    def __str__(self):
        return str(self.value)

    class Meta:
        verbose_name = "Звезда рейтинга"
        verbose_name_plural = "Звезды рейтинга"
        ordering = ("-value",)


class Rating(models.Model):
    """Рейтинг"""
    ip = models.CharField("IP адрес", max_length=90)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="фильм")
    star = models.ForeignKey(RatingStars, on_delete=models.CASCADE, verbose_name="звезда")

    def __str__(self):
        return f"{self.movie} - {self.star}"

    class Meta:
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"
        ordering = ("-star",)


class Review(models.Model):
    """Отзывы"""
    email = models.EmailField()
    name = models.CharField("Имя", max_length=90)
    text = models.TextField("Сообщение", max_length=5000)
    parent = models.ForeignKey(
        "self", verbose_name="Родитель", on_delete=models.SET_NULL, null=True, blank=True
    )
    movie = models.ForeignKey(Movie, verbose_name="фильм", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.movie} - {self.name}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
