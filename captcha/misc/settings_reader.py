import datetime
from typing import Any, Mapping, Tuple, Union

from pydantic import BaseModel, BaseSettings, validator
from data.config import CAPTCHA_DURATION, REDIS_URL
from captcha.misc.paths import BASE_DIR


# class BotSettings(BaseModel):
#     token: str


# class WebhookSettings(BaseModel):
#     host: str
#     path: str

#     @validator("host")
#     def host_to_url(cls, v: str) -> str:
#         if v.startswith("https"):
#             return v
#         return f"https://{v}"

#     @property
#     def url(self) -> str:
#         if self.host and self.path:
#             return f"{self.host}{self.path}"
#         return ""


# class WebAppSettings(BaseModel):
#     host: str
#     port: int


class RedisSettings(BaseModel):

    @property
    def connection_uri(self) -> str:
        return REDIS_URL


class CaptchaSettings(BaseModel):
    duration: Union[int, datetime.timedelta]

    @validator("duration")
    def to_timedelta(cls, v: Union[int, datetime.timedelta]) -> datetime.timedelta:
        v = CAPTCHA_DURATION
        if isinstance(v, datetime.timedelta):
            return v
        return datetime.timedelta(seconds=v)


class Settings(BaseSettings):
    # bot: BotSettings
    # webhook: WebhookSettings
    # webapp: WebAppSettings
    redis: RedisSettings
    captcha: CaptchaSettings
