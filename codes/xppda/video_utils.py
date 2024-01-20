import re
import os


range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)


class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


def convert_video(myfile, request):
    user = request.user
    fs = FileSystemStorage()
    user_hash = hashlib.sha1(
        user.email.encode('utf-8')
    ).hexdigest()
    uploaded_name = (
        "%s/%s-%s" % (user_hash, uuid.uuid4(), myfile.name)
    ).lower()

    filename = fs.save(uploaded_name, myfile)
    uploaded_file_url = fs.url(filename)
    print(uploaded_name)
    # this is android device
    if uploaded_name[-4:] == '.mov':
        # ffmpeg!
        uploaded_file_url = convert_file(uploaded_file_url)

    print(uploaded_file_url)
    # now lets create the db entry
    user = User.objects.get(id=user.id)
    video = VideoUpload.objects.create(
        videoUrl=uploaded_file_url, user=user
    )

    profile = get_user_profile(user)
    msg = (
        "<a href='https://%s'>Click to play</a>" %
        video.video_monitor_link()
    )

    if hasattr(profile, 'notify_email') and profile.notify_email:
        email_utils.send_raw_email(
            profile.notify_email,  # send report here
            user.email,  # replies to goes here
            'Video Checkin from %s' % profile.name,
            msg
        )

    url = 'https://hooks.slack.com/services/'
    url += 'TF6H12JQY/BFJHJFSN5/Zeodnz8HPIR4La9fq5J46dKF'
    domain_name = Site.objects.last().domain
    data = (
        str("VideoUpload: %s - https://%s%s" % (
            user.email,
            domain_name,
            uploaded_file_url)
            ))
    body = {"text": "%s" % data, 'username': 'pam-server'}
    requests.put(url, data=json.dumps(body))
    return video



