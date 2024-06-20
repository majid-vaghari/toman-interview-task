from django.contrib import admin

from .models import Transaction, Wallet


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'sender', 'receiver', 'amount', 'status')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'balance')
