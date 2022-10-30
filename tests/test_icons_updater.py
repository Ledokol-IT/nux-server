import pytest

import nux.models.app as mapp
from nux.icons_updater._icons_updater import update_icons_batch


@pytest.mark.skip("doesn't implement registration with password only")
def test_icons_updater(session, options):
    android_package_name = "com.robtopx.geometryjumplite"
    app_data = mapp.AppSchemeCreateAndroid(
        android_package_name=android_package_name,
        name="Geometry Dash",
        android_category=0,
    )
    with session.begin():
        query = session.query(mapp.App)
        query = query.where(
            mapp.App.icon_preview.is_(None))  # type: ignore
        query.delete()

    with session.begin():
        app = mapp.create_app_android(app_data)
        session.add(app)

    update_icons_batch()

    app: mapp.App = session.query(mapp.App).where(
        mapp.App.android_package_name == android_package_name).first()
    assert app is not None
    assert app.icon_preview is not None
