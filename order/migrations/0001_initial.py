# Generated by Django 2.2.7 on 2019-11-24 21:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fund', '0001_initial'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sponser', models.IntegerField(null=True)),
                ('stock', models.IntegerField(null=True)),
                ('quantity', models.IntegerField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='basket_project', to='fund.FundProject')),
                ('rewards', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='basket_reward', to='fund.FundReward')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='basket_user', to='account.User')),
            ],
            options={
                'db_table': 'baskets',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_support_agreed', models.BooleanField(null=True)),
                ('delivery_name', models.CharField(max_length=10, null=True)),
                ('delivery_number', models.CharField(max_length=12, null=True)),
                ('delivery_address', models.CharField(max_length=100, null=True)),
                ('delivery_request', models.CharField(max_length=20, null=True)),
                ('card_number', models.CharField(max_length=4, null=True)),
                ('card_period', models.CharField(max_length=10, null=True)),
                ('card_password', models.CharField(max_length=2, null=True)),
                ('card_birthday', models.CharField(max_length=10, null=True)),
                ('is_agreed', models.BooleanField(null=True)),
                ('basket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='order.Basket')),
                ('reward', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reward', to='fund.FundReward')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Order.user+', to='account.User')),
            ],
            options={
                'db_table': 'orders',
            },
        ),
    ]
