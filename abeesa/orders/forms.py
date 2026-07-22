from django import forms


class OrderItemQuantityForm(forms.Form):
    """One of these gets rendered per menu item, letting the customer pick a quantity."""
    quantity = forms.IntegerField(min_value=0, initial=0, required=False)