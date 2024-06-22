from django.contrib import admin

from .models import Transaction, Wallet


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'sender', 'receiver', 'amount', 'status')
    fields = ('uuid', 'sender', 'receiver', 'amount', 'scheduled_time', 'status', 'error_message', 'created', 'updated')

    readonly_fields = ['uuid', 'status', 'error_message', 'created', 'updated']

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'balance')
    fields = ('uuid', 'balance', 'created', 'updated')

    readonly_fields = ['uuid', 'balance', 'created', 'updated']
