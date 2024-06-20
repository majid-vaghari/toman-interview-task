from django.db import transaction

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response


from .models import Wallet, Transaction
from .serializers import WalletSerializer, DepositSerializer, WithdrawRequestSerializer
from .tasks import process_withdrawal


class WalletViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet,):
    queryset = Wallet.objects.all().order_by('-created')
    serializer_class = WalletSerializer

    @action(detail=True, methods=['patch'], serializer_class=DepositSerializer)
    def deposit(self, request, pk=None):
        deposit_request = self.get_serializer(data=request.data)
        deposit_request.is_valid(raise_exception=True)
        amount = deposit_request.validated_data['amount']

        with transaction.atomic():
            self.get_queryset() \
                .select_for_update() \
                .get(uuid=pk) \
                .deposit(amount)

        headers = self.get_success_headers({'uuid': pk})
        wallet = self.get_queryset().get(uuid=pk)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    @action(detail=True, methods=['post'], serializer_class=WithdrawRequestSerializer)
    def withdraw(self, request, pk=None):
        withdraw_request = self.get_serializer(data=request.data)
        withdraw_request.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                t = Transaction(
                    sender_id=pk,
                    receiver_id=withdraw_request.validated_data['target'],
                    amount=withdraw_request.validated_data['amount'],
                    scheduled_time=withdraw_request.validated_data['scheduled_time'],
                )
                t.full_clean()
                t.save()
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)



        headers = self.get_success_headers({'uuid': pk})
        wallet = self.get_queryset().get(uuid=pk)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
