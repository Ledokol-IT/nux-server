import random
import fastapi
import pydantic


class DefaultProfilePic(pydantic.BaseModel):
    id: str
    url: str


profile_pics_data = [
    DefaultProfilePic(
        id="Daniil",
        url="https://sun4.userapi.com/sun4-10/s/v1/ig2/sM6Y1IOU3zYFLOwpa8VAU9kMLGBpvko8oJkvliW3VvRpwJuNIONnkDrgQBg1FGjexOpQNUibqLPvWF-UrzAoDNkl.jpg?size=400x400&quality=95&crop=383,544,488,488&ava=1",  # noqa
    ),
    DefaultProfilePic(
        id="Gordey",
        url="https://sun1.userapi.com/sun1-23/s/v1/ig2/8hFbNRCkneQhaatGY40bd6Nuizjf9fNz7cUGguvmEzJyB16b-yzB1A4qIyixQIyhwlRs3E36eyn16ps9vs0Sj6iy.jpg?size=400x400&quality=95&crop=167,166,689,689&ava=1",  # noqa
    ),
]


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
