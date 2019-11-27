from django.db      import models
from account.models import Maker

class Document(models.Model):
    name = models.CharField(max_length= 20, null=True)

    class Meta:
        db_table = "documents"

class FundMainAgreement(models.Model):
    q1 = models.SmallIntegerField(null=True)
    q2 = models.SmallIntegerField(null=True)
    q3 = models.CharField(max_length = 100, null=True)
    q4 = models.CharField(max_length = 100, null=True)
    is_commision_agreed = models.BooleanField(default=False)
    is_futureopen_agreed = models.BooleanField(default=False)
    document = models.ForeignKey(Document,on_delete = models.CASCADE,
            related_name = 'fundmainagreements')
    maker = models.ForeignKey(Maker, on_delete = models.CASCADE)

    class Meta:
        db_table = "fundmainagreements"

class FundCategory(models.Model):
    name = models.CharField(max_length = 100, null=True)

    class Meta:
        db_table = "fundcategories"

class FundMainInformation(models.Model):
    title            = models.CharField(max_length = 50, null=True)
    goal_money       = models.IntegerField(null=True)
    main_image       = models.URLField(max_length=500, null=True, blank=True)
    category         = models.ForeignKey(FundCategory, on_delete = models.CASCADE,
        related_name = 'fundmaininformations')
    deadline         = models.DateField(null=True)
    is_adult_agreed = models.BooleanField(default=False)
    maker = models.ForeignKey(Maker, on_delete = models.CASCADE)

    class Meta:
        db_table = "fundmaininformations"


class PolicyDocument(models.Model):
    name = models.CharField(max_length = 1000)

    class Meta:
        db_table ="policydocumets"


class FundPolicy(models.Model):
    q1 = models.CharField(max_length = 100, null=True)
    q2 = models.IntegerField(null=True)
    q3 = models.CharField(max_length = 100, null=True)
    q4 = models.CharField(max_length = 100, null=True)
    is_auth_agreed = models.BooleanField(null=True)
    is_commision = models.BooleanField(null=True)
    is_opened = models.BooleanField(null=True)
    document = models.ForeignKey(PolicyDocument, on_delete = models.CASCADE)
    maker = models.ForeignKey(Maker, on_delete = models.CASCADE)

    class Meta:
        db_table = "fundpolicies"


class FundMaker(models.Model):
    company_name = models.CharField(max_length = 50, null=True)
    company_image = models.URLField(max_length=500, null=True)
    cs_email = models.CharField(max_length = 50, null=True)
    cs_number = models.CharField(max_length = 13,null=True)
    ceo_name = models.CharField(max_length = 50, null=True)
    ceo_email = models.CharField(max_length = 50, null=True)
    kakao_id = models.CharField(max_length = 50, null=True)
    kakao_link = models.CharField(max_length = 200, null=True)
    hompage = models.CharField(max_length = 500, null=True)
    sns1 = models.CharField(max_length = 100, null=True)
    sns2 = models.CharField(max_length = 100, null=True)
    sns3 = models.CharField(max_length = 100, null=True)
    maker = models.ForeignKey(Maker, on_delete = models.CASCADE)

    class Meta:
        db_table = "fundmakers"

class FundStory(models.Model):
    summary    = models.CharField(max_length=400, null=True)
    is_agreed  = models.BooleanField(null=True, default=False)
    context    = models.CharField(max_length =3000, null=True)
    maker      = models.ForeignKey(Maker, on_delete=models.CASCADE)

    class Meta:
        db_table = 'fundstories'

class StoryPhoto(models.Model):
    fund_story = models.ForeignKey(FundStory, on_delete=models.CASCADE,related_name='storyphotos')
    photo      = models.URLField(max_length=500, null=True)

    class Meta:
        db_table = 'storyphotos'

class FundProject(models.Model):
    fund_main_agreement      = models.OneToOneField(FundMainAgreement, on_delete = models.CASCADE)
    fund_main_information    = models.OneToOneField(FundMainInformation, on_delete = models.CASCADE)
    fund_policies            = models.OneToOneField(FundPolicy, on_delete = models.CASCADE)
    fund_makers              = models.OneToOneField(FundMaker, on_delete = models.CASCADE)
    maker                    = models.ForeignKey(Maker, on_delete = models.CASCADE)
    fund_story               = models.OneToOneField(FundStory, on_delete=models.CASCADE)

    class Meta:
        db_table = "fundprojects"

class FundReward(models.Model):
    seller_product_number = models.SmallIntegerField(null=True)
    name                  = models.CharField(max_length = 200, null = True)
    price                 = models.IntegerField(null= True)
    introduction          = models.CharField(max_length = 300, null = True)
    stock                 = models.IntegerField(null = True)
    delivery_fee          = models.IntegerField(null=True) 
    scheduled_date        = models.CharField(max_length=50, null=True)
    option                = models.CharField(max_length=50, null=True)
    maker                 = models.ForeignKey(Maker, on_delete = models.CASCADE, related_name = 'makers')
    project               = models.ForeignKey(FundProject, on_delete = models.CASCADE, related_name = 'fundrewards')
    class Meta:
        db_table = "fundrewards"
