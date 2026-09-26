from django.urls import path

from .views import (
    BudgetListCreateView,
    ExpenseListCreateView,
)


urlpatterns = [
    path(
        "budgets/",
        BudgetListCreateView.as_view(),
        name="budget-list-create",
    ),
    path(
        "expenses/",
        ExpenseListCreateView.as_view(),
        name="expense-list-create",
    ),
]