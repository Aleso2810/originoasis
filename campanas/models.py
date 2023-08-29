from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Modelo para Categorías de Campañas
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self)->str:
        return self.name

# Modelo para Campañas
class Campaign(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    photo = models.URLField(max_length=300)
    beneficiary = models.ForeignKey(User, on_delete=models.CASCADE)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    percentage_of_target = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Nueva columna
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')

    def __str__(self)->str:
        return self.name

    def is_open(self):
        """Verifica si la campaña está abierta"""
        return self.status == 'open' and self.end_date > timezone.now()

    def close_if_needed(self):
        """Cierra la campaña si ha pasado la fecha límite"""
        if self.end_date <= timezone.now():
            if self.end_date <= timezone.now():
                self.status = 'closed'
                self.save()

    def update_collected_amount(self):
        total_contributions = Contribution.objects.filter(campaign=self).aggregate(total=models.Sum('amount'))['total']
        self.collected_amount = total_contributions if total_contributions else 0
        # Actualizar el porcentaje con respecto a la meta
        if self.target_amount != 0:
            self.percentage_of_target = (self.collected_amount / self.target_amount) * 100
        else:
            self.percentage_of_target = 0
        self.save()

# Modelo para Aportes
class Contribution(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
    )

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.campaign.update_collected_amount()


# Modelo para Comentarios
class Comment(models.Model):
    """Guarda un comentario solo si el usuario ha contribuido a la campaña."""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    date = models.DateField(default=timezone.now)

    def __str__(self)->str:
        return f"{self.user.username} - {self.comment_text[:50]}"

    def save(self, *args, **kwargs):
        # Antes de guardar el comentario, verificamos si el usuario ha hecho una contribución a la campaña
        has_contributed = Contribution.objects.filter(user=self.user, campaign=self.campaign).exists()
        if not has_contributed:
            raise PermissionError("Solo Contribuyentes activos pueden comentar las campañas.")
        super(Comment, self).save(*args, **kwargs)
