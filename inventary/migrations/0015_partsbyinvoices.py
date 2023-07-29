# Generated by Django 4.1.7 on 2023-07-29 17:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventary', '0014_soldparts_part_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartsByInvoices',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventary.invoices')),
                ('sold_part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventary.soldparts')),
            ],
        ),
    ]
