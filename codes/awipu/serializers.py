from django.contrib.auth.models import User
from rest_framework import serializers

from dappx.models import UserProfileInfo, GpsCheckin, VideoUpload, UserMonitor, OrganizationMember, Organization


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name']


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = UserProfileInfo
        fields = ['user', 'user_org_id']


class GpsCheckinSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = GpsCheckin
        fields = ['msg', 'lat', 'lng', 'user']


class VideoUploadSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = VideoUpload
        fields = ['id', 'user', 'videoUrl']


class UserMonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMonitor
        fields = '__all__'

    def get_detailed_data(self, instance):
        return {
            'User': UserSerializer(instance.user).data,
            # 'Profile': UserProfileSerializer(instance.user).data
            # 'GPS': GpsCheckinSerializer(instance.gps_user.all(), many=True).data
            # 'Organization': OrganizationSerializer(instance.organization).data
        }

    def to_representation(self, instance):
        data = super(UserMonitorSerializer, self).to_representation(instance)
        data.update(self.get_detailed_data(instance))
        gps = GpsCheckin.objects.filter(user_id=instance.user_id)
        video = VideoUpload.objects.filter(user_id=instance.user_id)

        if gps is not None:
            Dict = {}
            num = 0
            for item in gps:

                if item.user_id == instance.user_id:
                    Dict["GPS_Location " + str(num)] = {
                        "type": "gps",
                        "long": item.lng,
                        "latitude": item.lat,
                        "message": item.msg}
                num = num + 1
            gps = {"gps": Dict}
            data.update(gps)
        if video is not None:
            Dict = {}
            num = 0
            for item in video:

                if item.user_id == instance.user_id:
                    Dict['video ' + str(num)] = {"type": "video",
                                                 "created_date": item.created_at,
                                                 "video_url": item.videoUrl}
                num = num + 1
            video = {"video": Dict}
            data.update(video)

        return data


class OrganizationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMember
        fields = '__all__'

    def get_detailed_data(self, instance):
        return {
            'User': UserSerializer(instance.user).data,
            'Organization': OrganizationSerializer(instance.organization).data,

        }

    def to_representation(self, instance):
        data = super(OrganizationMemberSerializer, self).to_representation(instance)
        data.update(self.get_detailed_data(instance))
        return data


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

