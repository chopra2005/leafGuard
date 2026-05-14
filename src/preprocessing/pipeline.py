from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class PreprocessConfig:
    target_size: tuple[int, int] = (224, 224)
    denoise_h: int = 10
    denoise_template_window_size: int = 7
    denoise_search_window_size: int = 21
    blur_kernel_size: tuple[int, int] = (5, 5)
    morph_kernel_size: tuple[int, int] = (5, 5)


class LeafPreprocessor:
    def __init__(self, config: PreprocessConfig | None = None) -> None:
        self.config = config or PreprocessConfig()

    def preprocess(self, image_bgr: np.ndarray) -> np.ndarray:
        resized = cv2.resize(image_bgr, self.config.target_size, interpolation=cv2.INTER_AREA)

        denoised = cv2.fastNlMeansDenoisingColored(
            resized,
            None,
            h=self.config.denoise_h,
            hColor=self.config.denoise_h,
            templateWindowSize=self.config.denoise_template_window_size,
            searchWindowSize=self.config.denoise_search_window_size,
        )

        segmented = self._segment_leaf(denoised)
        rgb = cv2.cvtColor(segmented, cv2.COLOR_BGR2RGB)
        return rgb

    def preprocess_from_path(self, image_path: str | Path) -> np.ndarray:
        image = cv2.imread(str(image_path))
        if image is None:
            raise FileNotFoundError(f"Could not read image: {image_path}")
        return self.preprocess(image)

    def _segment_leaf(self, image_bgr: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

        lower_green = np.array([20, 20, 20], dtype=np.uint8)
        upper_green = np.array([95, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_green, upper_green)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, self.config.morph_kernel_size)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.GaussianBlur(mask, self.config.blur_kernel_size, 0)

        segmented = cv2.bitwise_and(image_bgr, image_bgr, mask=mask)
        return segmented
