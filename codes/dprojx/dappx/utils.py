import datetime

def calc_days_sober(profile):
    if (profile and profile.sober_date and
            len(profile.sober_date.split("/")) == 3):
        today = datetime.date.today()

        year = int(profile.sober_date.split("/")[2])
        month = int(profile.sober_date.split("/")[0])
        day = int(profile.sober_date.split("/")[1])

        past = datetime.date(year, month, day)
        diff = today - past
        print (diff.days)
        return diff.days
