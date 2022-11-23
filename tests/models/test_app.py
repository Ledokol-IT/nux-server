import freezegun
from datetime import timedelta as td
from nux.utils import now

import nux.models.app as mapp
import nux.models.user as muser


def test_update_stats(session):
    user = muser.create_user(muser.UserSchemeCreate(
        nickname="user",
        name="User",
        phone="+79009009000"
    ))
    session.add(user)
    _, app1 = mapp.determine_app_android(session, mapp.AppSchemeCreateAndroid(
        android_package_name="app.package1",
        name="app1",
        android_category=0,
    ))
    _, app2 = mapp.determine_app_android(session, mapp.AppSchemeCreateAndroid(
        android_package_name="app.package2",
        name="app2",
        android_category=0,
    ))
    mapp.set_apps_to_user(
        session,
        user,
        [app1, app2],
    )
    session.commit()

    with freezegun.freeze_time("2012-01-14 12:00"):
        two_weeks_before_now = now() - td(days=14)
        mapp.add_user_in_app_record(
            session, user, app1,
            two_weeks_before_now - td(days=1),
            two_weeks_before_now + td(days=1),
        )
        mapp.add_user_in_app_record(
            session, user, app2,
            two_weeks_before_now + td(days=1),
            two_weeks_before_now + td(days=1, hours=12),
        )
        mapp.add_user_in_app_record(
            session, user, app2,
            two_weeks_before_now + td(days=2),
            two_weeks_before_now + td(days=3),
        )
        mapp.update_periodic_stats(session, user)
        apps_and_stats = mapp.get_user_apps_and_stats(
            session, user)
        assert len(apps_and_stats) == 2
        app1_stats = next(filter(lambda s: s.app == app1, apps_and_stats))
        app2_stats = next(filter(lambda s: s.app == app2, apps_and_stats))
        assert app1_stats.statistics.activity_last_two_weeks == td(days=1)
        assert app2_stats.statistics.activity_last_two_weeks == td(
            days=1, hours=12)
