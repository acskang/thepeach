from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from common.models import BaseModel

from .managers import UserManager


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    display_name = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    smartphone_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    external_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text="Reserved for external SSO subject or provider-specific identifier.",
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["created_at"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.full_name and not self.display_name:
            self.display_name = self.full_name
        elif self.display_name and not self.full_name:
            self.full_name = self.display_name
        super().save(*args, **kwargs)

    @property
    def company_ids(self):
        return self.company_memberships.values_list("company_id", flat=True)

    @property
    def department_ids(self):
        return self.department_memberships.values_list("department_id", flat=True)

    def belongs_to_company(self, company_id):
        if self.is_superuser:
            return True
        return self.company_memberships.filter(company_id=company_id).exists()

    def has_department_access(self, company_id):
        if self.is_superuser:
            return True
        return self.department_memberships.filter(department__company_id=company_id).exists()


class Company(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    code = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "company"
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class Department(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=200)
    code = models.SlugField(max_length=100)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["company__name", "name"]
        verbose_name = "department"
        verbose_name_plural = "departments"
        constraints = [
            models.UniqueConstraint(fields=["company", "code"], name="uniq_department_code_per_company"),
            models.UniqueConstraint(fields=["company", "name"], name="uniq_department_name_per_company"),
        ]

    def __str__(self):
        return f"{self.company.name} / {self.name}"


class UserCompanyMembership(BaseModel):
    ROLE_OWNER = "owner"
    ROLE_ADMIN = "admin"
    ROLE_MEMBER = "member"

    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_MEMBER, "Member"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="company_memberships")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="user_memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["company__name", "user__email"]
        verbose_name = "user company membership"
        verbose_name_plural = "user company memberships"
        constraints = [
            models.UniqueConstraint(fields=["user", "company"], name="uniq_user_company_membership"),
        ]

    def __str__(self):
        return f"{self.user.email} @ {self.company.name}"


class UserDepartmentMembership(BaseModel):
    ROLE_ADMIN = "admin"
    ROLE_MANAGER = "manager"
    ROLE_MEMBER = "member"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_MANAGER, "Manager"),
        (ROLE_MEMBER, "Member"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="department_memberships")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="user_memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)

    class Meta:
        ordering = ["department__company__name", "department__name", "user__email"]
        verbose_name = "user department membership"
        verbose_name_plural = "user department memberships"
        constraints = [
            models.UniqueConstraint(fields=["user", "department"], name="uniq_user_department_membership"),
        ]

    def __str__(self):
        return f"{self.user.email} @ {self.department}"
