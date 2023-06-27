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

    TITLE_CONDITIONS = (
        ('CLEAN', 'Clean'),
        ('SALVAGE', 'Salvage'),
        ('DISTRACTION', 'Distraction')
    )

    id = models.AutoField(primary_key = True)
    brand = models.ForeignKey(Brands, on_delete = models.CASCADE, null = True)
    model = models.ForeignKey(Models, on_delete = models.CASCADE, null = True)
    year = models.IntegerField(default = 2000)
    inventary_number = models.CharField(max_length = 25, null = True)
    vin_number = models.CharField(max_length=17, default = '00')
    title_condition = models.CharField(choices=TITLE_CONDITIONS, max_length=11, default='Clean')
    cost = models.FloatField(default=1000.00)
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
    out = models.BooleanField(default=False)
    date_out = models.DateField(null = True)

    def __str__(self):
        return f'{self.car.model.name} - {self.car.brand.name} {self.car.inventary_number}'

class CarsOut(models.Model):
    id = models.AutoField(primary_key = True)
    car = models.ForeignKey(Cars, on_delete = models.CASCADE) 
    date_out = models.DateField()

    def __str__(self):
        return f'{self.car.model.name} - {self.car.brand.name} {self.car.inventary_number}'
    

class RemoveParts(models.Model):
    id = models.AutoField(primary_key=True)
    car = models.ForeignKey(Cars, on_delete=models.CASCADE)
    rims = models.IntegerField()
    tires = models.IntegerField()
    engine = models.BooleanField()
    catalyst = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Rims: {self.rims} --- Tires: {self.tires} --- Catalyst: {self.catalyst} --- Engine: {self.engine}'
    

class SoldParts(models.Model):
    PART_TYPE = (
        ('Tires', 'Tires'),
        ('Rims', 'Rims'),
        ('Engines', 'Engines'),
        ('Catalyst', 'Catalyst'),
        ('Others', 'Others')
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=60)
    car = models.ForeignKey(Cars, on_delete=models.CASCADE, blank=True, null=True)
    part_type = models.CharField(choices=PART_TYPE, max_length=8)
    buyer = models.ForeignKey(Buyers, on_delete=models.CASCADE)
    sold_date = models.DateField()
    add_date = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    price = models.FloatField()

    def __str__(self):
        return f'{self.part_type} --- quantity: {self.quantity}'
    

class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    tires = models.IntegerField(default=0)
    rims = models.IntegerField(default=0)
    catalysts = models.IntegerField(default=0)
    engines = models.IntegerField(default=0)
    scratched_cars = models.IntegerField(default=0)
    last_update = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Tires: {self.tires} Rims: {self.rims} Catalysts: {self.catalysts} Engines: {self.engines} Scratched_Cars: {self.scratched_cars}'


class Customer(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField()
    description = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)
    