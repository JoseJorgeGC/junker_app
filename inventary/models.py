from django.db import models

# Create your models here.
class Brands(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=100, verbose_name = "brand name")

    def __str__(self):
        return self.name


class Models(models.Model):
    id = models.AutoField(primary_key = True)
    brand = models.ForeignKey(Brands, on_delete=models.CASCADE)
    name = models.CharField(max_length = 100, verbose_name = "model name")

    def __str__(self):
        return f'{self.brand.name} - {self.name}'



class Cars(models.Model):
    CONDITIONS = (
        ('GOOD', 'GOOD'),
        ('MEDIUM', 'MEDIUM'),
        ('BAD', 'BAD')
    )

    id = models.AutoField(primary_key = True)
    brand = models.ForeignKey(Brands, on_delete = models.CASCADE, null = True)
    model = models.ForeignKey(Models, on_delete = models.CASCADE, null = True)
    year = models.IntegerField(default = 2000)
    inventary_number = models.CharField(max_length = 25, null = True)
    condition = models.CharField(choices = CONDITIONS, max_length = 6)
    entry_date = models.DateField(null = True)
    title = models.FileField(upload_to="media/titles/", null = True)
    image = models.ImageField(upload_to="static/cars/", null = True)
    waiting = models.BooleanField(default = True)

    def __str__(self):
        return f'{self.brand.name} - {self.model.name} {self.inventary_number}'

    def delete(self, using=None, keep_parents=False):
        self.image.storage.delete(self.image.name)
        self.title.storage.delete(self.title.name)
        super().delete()

class Buyers(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    dni = models.CharField(max_length = 20)
    phone_number = models.CharField(max_length = 20, null = True)

    def __str__(self):
        return f'{self.name} - {self.last_name}'

class SoldCars(models.Model):
    id = models.AutoField(primary_key = True)
    car = models.ForeignKey(Cars, on_delete = models.CASCADE)
    buyer = models.ForeignKey(Buyers, on_delete = models.CASCADE)
    price = models.FloatField(max_length = 10)
    date = models.DateField()

    def __str__(self):
        return f'{self.car.model.name} - {self.car.brand.name} {self.car.inventary_number}'

class JunkCars(models.Model):
    id = models.AutoField(primary_key = True)
    car = models.ForeignKey(Cars, on_delete = models.CASCADE)
    to_junk_date = models.DateField(auto_now_add = True)
    scratched_date = models.DateField(null = True)
    waiting = models.BooleanField(default = True)

    def __str__(self):
        return f'{self.car.model.name} - {self.car.brand.name} {self.car.inventary_number}'

class CarsOut(models.Model):
    id = models.AutoField(primary_key = True)
    car = models.ForeignKey(Cars, on_delete = models.CASCADE) 
    date_out = models.DateField()

    def __str__(self):
        return f'{self.car.model.name} - {self.car.brand.name} {self.car.inventary_number}'