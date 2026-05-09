from io import BytesIO
from typing import IO
from PIL import Image
from PIL.ImageFile import ImageFile
import cv2, numpy as np


class ImageProcessing:
    def __init__(self):
        self._origin_image: ImageFile = None
        self._transformed_image: ImageFile = None

    def process_image(self, image_data: IO[bytes]):
        self._origin_image = Image.open(image_data)
        self._transformed_image = self.__optimise()

    def get_transformed_image_bytes(self) -> BytesIO:
        if self._transformed_image is None:
            raise ValueError("Image has not been processed yet.")

        buffer = BytesIO()
        self._transformed_image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    def get_origin_image_bytes(self) -> BytesIO:
        if self._origin_image is None:
            raise ValueError("Image has not been processed yet.")

        buffer = BytesIO()
        self._origin_image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    def get_origin_image(self) -> ImageFile:
        if self._origin_image is None:
            raise ValueError("Image has not been processed yet.")

        return self._origin_image

    def get_transformed_image(self) -> ImageFile:
        if self._transformed_image is None:
            raise ValueError("Image has not been processed yet.")

        return self._transformed_image
    
    def __optimise(self) -> ImageFile:
        transformed_image = self._origin_image.convert("L")

        #img = np.array(transformed_image, dtype=np.uint8)
        #blur = cv2.GaussianBlur(img, (3, 3), 0)
        #binary = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 8)
        
        return transformed_image
