from django.db import models

class ProfileInterest(models.Model):
    education_kids         = models.BooleanField()
    fashion_beauty_goods   = models.BooleanField()
    home_design_item       = models.BooleanField()
    concert_culture        = models.BooleanField()
    sport_mobility         = models.BooleanField()
    publishing             = models.BooleanField()
    animal                 = models.BooleanField()
    tech_home_appliance    = models.BooleanField()

    class Meta:
        db_table = 'profileinterests'

class SocialPlatform(models.Model):
    platform = models.CharField(max_length=20, default=1)

    class Meta:
        db_table = 'social_platform'

class User(models.Model):
    email            = models.CharField(max_length=255, unique=True)
    user_name        = models.CharField(max_length=150, null=True, blank=True)
    password         = models.CharField(max_length=300, null=True, blank=True)
    phone_number     = models.CharField(max_length=20, null=True)
    is_agree         = models.BooleanField(null=True)
    is_maker         = models.BooleanField(null=True)
    promotion        = models.BooleanField(null=True)
    phone_number     = models.CharField(max_length=20, null=True)
    social           = models.ForeignKey(SocialPlatform, on_delete=models.CASCADE, null=True, related_name='user_social', default=1)
    social_login_id  = models.CharField(max_length=100, null=True)
    profile_photo    = models.URLField(max_length=500, null=True, blank=True)
    company          = models.CharField(max_length=100, null=True, blank=True)
    company_position = models.CharField(max_length=50, null=True, blank=True)
    university       = models.CharField(max_length=50, null=True, blank=True)
    major            = models.CharField(max_length=50, null=True, blank=True)
    main_address     = models.CharField(max_length=50, null=True, blank=True)
    sub_address      = models.CharField(max_length=50, null=True, blank=True)
    introduction     = models.CharField(max_length=1200, null=True, blank=True)
    user_interest    = models.ManyToManyField(ProfileInterest, through='UserGetInterest')

    class Meta:
        db_table = 'users'

class UserGetInterest(models.Model):
	user             = models.ForeignKey(User, on_delete=models.CASCADE)
	profile_interest = models.ForeignKey(ProfileInterest, on_delete=models.CASCADE)

	class Meta:
		db_table = 'usergetinterests'

class Maker(models.Model):
    user             = models.OneToOneField(User, on_delete=models.CASCADE, related_name='users')
    name             = models.CharField(max_length=150)
    kind             = models.CharField(max_length=150)
    phone_number     = models.CharField(max_length=30)
    is_agreed        = models.BooleanField()

    class Meta:
        db_table = 'makers'
