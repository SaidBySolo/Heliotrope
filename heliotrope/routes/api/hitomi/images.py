from sanic import Blueprint
from sanic.response import json
from sanic.views import HTTPMethodView

from heliotrope.database.query import get_galleryinfo
from heliotrope.utils.hitomi.common import image_url_from_image
from heliotrope.utils.hitomi.models import HitomiGalleryInfoModel
from heliotrope.utils.response import not_found
from heliotrope.utils.shuffle import shuffle_image_url
from heliotrope.utils.typed import HeliotropeRequest

hitomi_images = Blueprint("hitomi_images", url_prefix="/images")


class HitomiImagesInfoView(HTTPMethodView):
    async def get(self, request: HeliotropeRequest, index):
        galleryinfo_json = await get_galleryinfo(index)
        if not galleryinfo_json:
            galleryinfo = await request.app.ctx.hitomi_requester.get_galleryinfo(index)
            if not galleryinfo:
                return not_found
        else:
            galleryinfo = HitomiGalleryInfoModel.parse_galleryinfo(galleryinfo_json)
        return json(
            {
                "files": [
                    {
                        "name": file.name,
                        "image": shuffle_image_url(
                            image_url_from_image(int(galleryinfo.galleryid), file, True)
                        ),
                    }
                    for file in galleryinfo.files
                ]
            }
        )


hitomi_images.add_route(HitomiImagesInfoView.as_view(), "/<index:int>")