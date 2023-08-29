from django.db import models

class DailyGeneralStats(models.Model):
    date = models.DateField(auto_now=True)
    total_items = models.IntegerField()
    total_quantity = models.IntegerField()
    total_cost = models.DecimalField(max_digits=9, decimal_places=2,
                                    help_text='This refers to the total cost of all items in the inventory. Each item quantity multiply by the cost per unit.')
    total_moving_items = models.IntegerField(blank=True, null=True)
    total_moving_quantity = models.IntegerField(blank=True, null=True)
    total_moving_cost = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    total_additions = models.IntegerField()
    total_add_cost = models.DecimalField(max_digits=9, decimal_places=2)
    total_subtractions = models.IntegerField()
    total_expense = models.DecimalField(max_digits=9, decimal_places=2,
                                    help_text='This refers to the total cost of all items that were subtracted from the inventory.')
