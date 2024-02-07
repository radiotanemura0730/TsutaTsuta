from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models



def validate_postal_code(value):
    # 郵便番号のバリデーションロジック
    if not value.isdigit() or len(value) != 7:
        raise ValidationError(("郵便番号は7桁の数字で入力してください。"), code="invalid_postal_code")


def validate_number(value):
    # 番地と電話番号のバリデーションロジック
    if not value.replace("-", "").isdigit():
        raise ValidationError(
            ("数字とハイフンのみを含む形式で入力してください。"),
            code="invalid_building_number",
        )


class Class(models.Model):
    lecture = models.CharField(max_length=20)


class CustomUser(AbstractUser):
    # 書き換え
    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email address"), unique=True, blank=True)
    #認証
    # auth_number = models.IntegerField()

    Soujin = "総合人間学部"
    Literature = "文学部"
    Education = "教育学部"
    Law = "法学部"
    Economics = "経済学部"
    Science = "理学部"
    Medic = "医学部"
    Pharmacy = "薬学部"
    Engineer = "工学部"
    Agriculture = "農学部"

    Soujin_gakka = "総合人間学科"
    Literature_gakka = "人文学科"
    Education_gakka = "教育科学科"
    Economics_gakka = "経済経営学科"
    Science_gakka = "理学科"
    Doctor = "医学科"
    Health = "人間健康科学科"
    Pharmacy_science = "薬科学科"
    Pharmacy_department = "薬学科"
    Earth = "地球工学科"
    Architecture = "建築学科"
    Physics = "物理工学科"
    Electric = "電気電子工学科"
    Information = "情報学科"
    Engineer_science = "工業化学科"
    Resource = "資源生物科学科"
    Biomedic = "応用生命科学科"
    Local_environment = "地域環境工学科"
    Food_environment = "食料・環境経済学科"
    Forestry = "森林科学科"
    Food_biology = "食品生物化学科"

    FACULTY_CHOICES = [
        (Soujin, "総合人間学部"),
        (Literature, "文学部"),
        (Education, "教育学部"),
        (Law, "法学部"),
        (Economics, "経済学部"),
        (Science, "理学部"),
        (Medic, "医学部"),
        (Pharmacy, "薬学部"),
        (Engineer, "工学部"),
        (Agriculture, "農学部"),
    ]

    DEPARTMENT_CHOICES = [
        (Soujin_gakka, "総合人間学科"),
        (Literature_gakka, "人文学科"),
        (Education_gakka, "教育科学科"),
        (Economics_gakka, "経済経営学科"),
        (Science_gakka, "理学科"),
        (Doctor, "医学科"),
        (Health, "人間健康科学科"),
        (Pharmacy_science, "薬科学科"),
        (Pharmacy_department, "薬学科"),
        (Earth, "地球工学科"),
        (Architecture, "建築学科"),
        (Physics, "物理工学科"),
        (Electric, "電気電子工学科"),
        (Information, "情報学科"),
        (Engineer_science, "工業化学科"),
        (Resource, "資源生物科学科"),
        (Biomedic, "応用生命科学科"),
        (Local_environment, "地域環境工学科"),
        (Food_environment, "食料・環境経済学科"),
        (Forestry, "森林科学科"),
        (Food_biology, "食品生物化学科"),
    ]

    user_id = models.CharField(max_length=20)
    birth_date = models.DateField(null=True, blank=True)
    introduce = models.TextField(blank=True)
    icon = models.ImageField(upload_to="uploads/images/")
    gakubu = models.CharField(max_length=20, choices=FACULTY_CHOICES, default=Soujin)
    gakka = models.CharField(
        max_length=20, choices=DEPARTMENT_CHOICES, default=Soujin_gakka
    )
    point = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class Address(models.Model):
    TOKYO = "13"
    KANAGAWA = "14"
    SAITAMA = "11"
    CHIBA = "12"
    OSAKA = "27"
    HYOGO = "28"
    KYOTO = "26"
    NARA = "29"
    HOKKAIDO = "01"
    AOMORI = "02"
    IWATE = "03"
    MIYAGI = "04"
    AKITA = "05"
    YAMAGATA = "06"
    FUKUSHIMA = "07"
    IBARAKI = "08"
    TOCHIGI = "09"
    GUNMA = "10"
    YAMANASHI = "19"
    NAGANO = "20"
    NIIGATA = "15"
    TOYAMA = "16"
    ISHIKAWA = "17"
    FUKUI = "18"
    YAMAGUCHI = "35"
    TOKUSHIMA = "36"
    KAGAWA = "37"
    EHIME = "38"
    KOCHI = "39"
    FUKUOKA = "40"
    SAGA = "41"
    NAGASAKI = "42"
    KUMAMOTO = "43"
    OITA = "44"
    MIYAZAKI = "45"
    KAGOSHIMA = "46"
    OKINAWA = "47"

    PREFECTURE_CHOICES = [
        (TOKYO, "東京都"),
        (KANAGAWA, "神奈川県"),
        (SAITAMA, "埼玉県"),
        (CHIBA, "千葉県"),
        (OSAKA, "大阪府"),
        (HYOGO, "兵庫県"),
        (KYOTO, "京都府"),
        (NARA, "奈良県"),
        (HOKKAIDO, "北海道"),
        (AOMORI, "青森県"),
        (IWATE, "岩手県"),
        (MIYAGI, "宮城県"),
        (AKITA, "秋田県"),
        (YAMAGATA, "山形県"),
        (FUKUSHIMA, "福島県"),
        (IBARAKI, "茨城県"),
        (TOCHIGI, "栃木県"),
        (GUNMA, "群馬県"),
        (YAMANASHI, "山梨県"),
        (NAGANO, "長野県"),
        (NIIGATA, "新潟県"),
        (TOYAMA, "富山県"),
        (ISHIKAWA, "石川県"),
        (FUKUI, "福井県"),
        (YAMAGUCHI, "山口県"),
        (TOKUSHIMA, "徳島県"),
        (KAGAWA, "香川県"),
        (EHIME, "愛媛県"),
        (KOCHI, "高知県"),
        (FUKUOKA, "福岡県"),
        (SAGA, "佐賀県"),
        (NAGASAKI, "長崎県"),
        (KUMAMOTO, "熊本県"),
        (OITA, "大分県"),
        (MIYAZAKI, "宮崎県"),
        (KAGOSHIMA, "鹿児島県"),
        (OKINAWA, "沖縄県"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    first_name_kana = models.CharField(max_length=20)
    last_name_kana = models.CharField(max_length=20)
    post = models.CharField(max_length=7, validators=[validate_postal_code])
    prefecture = models.CharField(max_length=2, choices=PREFECTURE_CHOICES, unique=True)
    city = models.CharField(max_length=50)
    house_number = models.CharField(max_length=50, validators=[validate_number])
    building = models.CharField(max_length=10)
    phone = models.CharField(max_length=10, validators=[validate_number])


class Product(models.Model):
    great = "新品・未使用"
    good = "目立った汚れなし"
    normal = "やや傷、汚れあり"
    bad = "状態が悪い"

    Soujin = "総合人間学部"
    Literature = "文学部"
    Education = "教育学部"
    Law = "法学部"
    Economics = "経済学部"
    Science = "理学部"
    Medic = "医学部"
    Pharmacy = "薬学部"
    Engineer = "工学部"
    Agriculture = "農学部"

    Soujin_gakka = "総合人間学科"
    Literature_gakka = "人文学科"
    Education_gakka = "教育科学科"
    Economics_gakka = "経済経営学科"
    Science_gakka = "理学科"
    Doctor = "医学科"
    Health = "人間健康科学科"
    Pharmacy_science = "薬科学科"
    Pharmacy_department = "薬学科"
    Earth = "地球工学科"
    Architecture = "建築学科"
    Physics = "物理工学科"
    Electric = "電気電子工学科"
    Information = "情報学科"
    Engineer_science = "工業化学科"
    Resource = "資源生物科学科"
    Biomedic = "応用生命科学科"
    Local_environment = "地域環境工学科"
    Food_environment = "食料・環境経済学科"
    Forestry = "森林科学科"
    Food_biology = "食品生物化学科"

    FACULTY_CHOICES = [
        (Soujin, "総合人間学部"),
        (Literature, "文学部"),
        (Education, "教育学部"),
        (Law, "法学部"),
        (Economics, "経済学部"),
        (Science, "理学部"),
        (Medic, "医学部"),
        (Pharmacy, "薬学部"),
        (Engineer, "工学部"),
        (Agriculture, "農学部"),
    ]

    DEPARTMENT_CHOICES = [
        (Soujin_gakka, "総合人間学科"),
        (Literature_gakka, "人文学科"),
        (Education_gakka, "教育科学科"),
        (Economics_gakka, "経済経営学科"),
        (Science_gakka, "理学科"),
        (Doctor, "医学科"),
        (Health, "人間健康科学科"),
        (Pharmacy_science, "薬科学科"),
        (Pharmacy_department, "薬学科"),
        (Earth, "地球工学科"),
        (Architecture, "建築学科"),
        (Physics, "物理工学科"),
        (Electric, "電気電子工学科"),
        (Information, "情報学科"),
        (Engineer_science, "工業化学科"),
        (Resource, "資源生物科学科"),
        (Biomedic, "応用生命科学科"),
        (Local_environment, "地域環境工学科"),
        (Food_environment, "食料・環境経済学科"),
        (Forestry, "森林科学科"),
        (Food_biology, "食品生物化学科"),
    ]

    CONDITION_CHOICES = [
        (great, "新品、未使用"),
        (good, "目立った汚れなし"),
        (normal, "やや傷、汚れあり"),
        (bad, "状態が悪い"),
    ]

    product_name = models.CharField(max_length=255)
    description = models.TextField()
    stripe_product_id = models.CharField(max_length=100)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=100)
    image = models.ImageField(upload_to="uploads/images/")
    gakubu_category = models.CharField(
        max_length=20, choices=FACULTY_CHOICES, default=Soujin
    )
    gakka_category = models.CharField(
        max_length=20, choices=DEPARTMENT_CHOICES, default=Soujin_gakka
    )
    classroom_category = models.ForeignKey(
        Class, on_delete=models.CASCADE, null=True, blank=True
    )
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.product_name


class Transaction(models.Model):
    buyer = models.ForeignKey(
        CustomUser, related_name="bought_product", on_delete=models.CASCADE
    )
    seller = models.ForeignKey(
        CustomUser, related_name="sold_product", on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    delivery_date = models.DateTimeField()
    deliver_fee = models.CharField(max_length=20)
    deliver_address = models.ForeignKey(
        Address, related_name="delivered_product", on_delete=models.CASCADE
    )
    is_shipped = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # 現在の日時を取得
        current_datetime = datetime.now()

        # 5日後の日時を計算
        future_datetime = current_datetime + timedelta(days=5)

        # モデルのフィールドに値を設定
        self.delivery_date = future_datetime

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.buyer.username} bought {self.product.product_name} from {self.seller.username}"


class Comment(models.Model):
    product = models.ForeignKey(
        Product, related_name="comments", on_delete=models.CASCADE
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def create(self):
        self.created_date = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.text}"


class Draft(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    is_created = models.BooleanField(default=False)

    def create(self):
        if not self.is_created:
            # 新しい Product インスタンスを作成して保存
            product = Product.objects.create(
                product_name=self.product.product_name,
                description=self.product.description,
                condition=self.product.condition,
                price=self.product.price,
                image=self.product.image,
                gakubu_category=self.product.gakubu_category,
                gakka_category=self.product.gakka_category,
                seller=self.product.seller,
            )
            self.product = product
            self.is_created = True
            self.save()

    def delete_created_product(self):
        if self.is_published:
            self.delete()

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} likes {self.product.product_name}"


class Review(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    evaluate = models.IntegerField(
        validators=[
            MaxValueValidator(5),  # 最大値を5に設定
            MinValueValidator(1),  # 最小値を1に設定
        ]
    )
    comment = models.TextField(max_length=200)
