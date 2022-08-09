import logging
import random
import re

import fastapi
import pydantic

import nux.s3

logger = logging.getLogger(__name__)


class DefaultProfilePic(pydantic.BaseModel):
    id: str
    url: str


def _fetch_profile_data():
    try:
        urls = nux.s3.list_objects("default_icons", "avatar_profile")
    except nux.s3.S3NotInitializedError:
        return [DefaultProfilePic(
            id="pic",
            url="http://example.com/pic.png",
        )]

    data = []
    for url in urls:
        try:
            id = re.fullmatch(r".+/([\w\d_]+)\.\w+", url)
            assert id is not None
            id = id.group(1)
            data.append(DefaultProfilePic(
                id=id,
                url=url,
            ))
        except Exception as e:
            logger.critical(f"can't parse {url}")
            logger.exception(e)
    return data


def setup():
    global profile_pics_data, profile_pics_ids, profile_pics_dict
    profile_pics_data = _fetch_profile_data()

    profile_pics_dict = {p.id: p for p in profile_pics_data}
    profile_pics_ids = list(profile_pics_dict.keys())


router = fastapi.APIRouter(prefix="/default_profile_pics")


class GetDefaultProfilePicsResponseScheme(pydantic.BaseModel):
    default_profile_pics: list[DefaultProfilePic]


@router.get("/list", response_model=GetDefaultProfilePicsResponseScheme)
def get_default_profile_pics_list():
    return {
        "default_profile_pics": profile_pics_data,
    }


def get_url_by_id(id: str) -> str:
    return profile_pics_dict[id].url


def get_random_id() -> str:
    return random.choice(profile_pics_ids)
