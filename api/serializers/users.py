from rest_framework import serializers


class UsersSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    email = serializers.EmailField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    is_project_manager = serializers.SerializerMethodField()
    is_account_manager = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    member_since = serializers.SerializerMethodField()


    def get_is_project_manager(self, obj):
        return obj.groups.filter(name='Project Managers').exists()

    def get_is_account_manager(self, obj):
        return obj.groups.filter(name='Account Managers').exists()

    def get_avatar(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None

    def get_customer_name(self, obj):
        if obj.profile.customer:
            return obj.profile.customer.name
        return None

    def get_vendor_name(self, obj):
        if obj.profile.vendor:
            return obj.profile.vendor.name
        return None

    def get_location(self, obj):
        return obj.profile.location

    def get_phone_number(self, obj):
        if obj.profile.phone_number:
            return obj.profile.phone_number.as_e164

        return None

    def get_member_since(self, obj):
        return obj.date_joined

    class Meta:
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'is_project_manager',
            'is_account_manager',
            'groups',
            'avatar',
            'customerName',
            'vendorName',
            'phone_number'
        )