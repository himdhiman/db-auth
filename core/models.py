from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from cloudinary.models import CloudinaryField
import threading, random
from core.helper import delete_cloudinary_image, create_user_notifcation


class UserProfile(models.Model):
    email = models.EmailField(verbose_name="email", unique=True, max_length=60)
    score = models.IntegerField(blank=True, null=True, default=0)
    rank = models.IntegerField(blank=True, null=True, default=0)
    rating = models.IntegerField(blank=True, null=True, default=0)
    hard_solved = models.IntegerField(blank=True, null=True, default=0)
    medium_solved = models.IntegerField(blank=True, null=True, default=0)
    easy_solved = models.IntegerField(blank=True, null=True, default=0)
    submissions = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.email


class StaticData(models.Model):
    easy = models.IntegerField(blank=True, null=True, default=0)
    medium = models.IntegerField(blank=True, null=True, default=0)
    hard = models.IntegerField(blank=True, null=True, default=0)
    avatar_count = models.IntegerField(blank=True, null=True, default=0)
    users_count = models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return "Fixed Data"


class Avatar(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    image = CloudinaryField("image")

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, username, password=None):
        if not email:
            raise ValueError("User must have an email address")
        if not first_name:
            raise ValueError("User must have a First Name")
        if not last_name:
            raise ValueError("User must have a Last Name")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, username, password=None):
        if not email:
            raise ValueError("User must have an email address")
        if not first_name:
            raise ValueError("User must have a First Name")
        if not last_name:
            raise ValueError("User must have a Last Name")

        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True

        user.save(using=self._db)
        profile_obj = UserProfile(email=user.email)
        profile_obj.save()
        threading.Thread(
            target=create_user_notifcation,
            kwargs={"email": self.normalize_email(email), "create": True, "username": username},
        ).start()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    AUTH_PROVIDERS = {
        "facebook": "facebook",
        "twitter": "twitter",
        "email": "email",
        "google": "google",
    }
    email = models.EmailField(verbose_name="email", unique=True, max_length=60)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    username = models.CharField(max_length=30, unique=True)
    profile_pic = models.TextField(blank=True, null=True)
    joining_Date = models.DateField(auto_now=True, verbose_name="date joined")
    last_login = models.DateField(auto_now=True, verbose_name="last login")
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    auth_provider = models.CharField(
        max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get("email")
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class AccountVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=20)

    def __str__(self):
        return self.user.email


class PasswordChange(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    pass_slug = models.CharField(max_length=20)

    def __str__(self):
        return self.user.email


@receiver(post_save, sender=CustomUser)
def after_creating_user(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.auth_provider != "email":
        threading.Thread(
            target=create_user_notifcation,
            kwargs={"email": instance.email, "create": True, "username": instance.username},
        ).start()
    obj = StaticData.objects.all().first()
    setattr(obj, "users_count", obj.users_count + 1)
    obj.save()
    num = random.randint(0, obj.avatar_count - 1)
    avatar_objs = Avatar.objects.all()
    setattr(instance, "profile_pic", avatar_objs[num].image.url)
    instance.save()
    return


@receiver(pre_delete, sender=CustomUser)
def before_deleting_user(sender, instance, *args, **kwargs):
    UserProfile.objects.filter(email=instance.email).delete()
    threading.Thread(
        target=create_user_notifcation,
        kwargs={
            "email": instance.email,
            "create": False,
            "username": instance.username,
        },
    ).start()
    obj = StaticData.objects.all().first()
    setattr(obj, "users_count", obj.users_count - 1)
    obj.save()
    return


@receiver(post_save, sender=Avatar)
def after_creating_avatar(sender, instance, *args, **kwargs):
    obj = StaticData.objects.all().first()
    setattr(obj, "avatar_count", obj.avatar_count + 1)
    obj.save()
    return


@receiver(pre_delete, sender=Avatar)
def before_deleting_avatar(sender, instance, *args, **kwargs):
    obj = StaticData.objects.all().first()
    setattr(obj, "avatar_count", obj.avatar_count - 1)
    obj.save()
    threading.Thread(
        target=delete_cloudinary_image, args=(instance.image.public_id,)
    ).start()
    return
