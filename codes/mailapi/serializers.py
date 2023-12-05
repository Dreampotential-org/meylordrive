from mailapi.models import Mail, Account
from rest_framework import serializers


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'email', 'active_on_server', 'password', )
        read_only_fields = ('active_on_server',)


class MailSerializer(serializers.HyperlinkedModelSerializer):
    account = AccountSerializer(many=False, read_only=True)

    class Meta:
        model = Mail
        fields = (
            'id', 'message_id', 'subject', 'message', 'row_date',
            'local_date', 'account'
        )
