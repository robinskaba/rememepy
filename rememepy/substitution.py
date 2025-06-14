from PIL import Image
from .supporting_functions import *


class Generator:
    def __init__(self):
        self.last_placement_position = None
        self.last_resized_substitute = None
        self.last_template = None

    def substitute(self, source_img_path: str, substitute_img_path: str,
                   dominant_cluster_amount: int = 6,
                   resize_to: tuple | None = None) -> Image.Image:
        """
        Replaces a region of the source image with a substitute image and returns the resulting image.

        This method analyzes the source image to find an appropriate area to replace—either based on
        a dominant color (using k-means clustering if `dominant_cluster_amount` > 0) or a default background
        color (white, if `dominant_cluster_amount` == 0). It then resizes the substitute image to fit the
        identified region and pastes it into the source image.

        Args:
            source_img_path (str): Path to the original image to modify.
            substitute_img_path (str): Path to the image to paste into the source.
            dominant_cluster_amount (int, optional): Number of clusters to use when identifying
                the dominant color. If 0, white is used as the dominant color. Defaults to 3.
            resize_to (tuple, optional): If provided, explicitly resizes the substitute image to this
                size (width, height) before pasting. If None, it resizes based on the detected area.

        Returns:
            PIL.Image.Image: The modified source image with the substitute image pasted in.
        """

        template = Image.open(source_img_path)
        substitute = Image.open(substitute_img_path)

        if resize_to:
            resized_substitute = substitute.resize(resize_to)
            placement_position = (0, 0)  # if manual resize, default placement
        else:
            dominant_color = (255, 255, 255) if dominant_cluster_amount == 0 else find_dominant_color(template,
                                                                                                dominant_cluster_amount)
            placement_position, new_size = find_placement(template, dominant_color)
            resized_substitute = substitute.resize(new_size)

        template.paste(resized_substitute, placement_position)

        # save state for validation
        self.last_placement_position = placement_position
        self.last_resized_substitute = resized_substitute
        self.last_template = template

        return template

    def validate_last_substitution(self, threshold_min: float = 0.1, threshold_max: float = 0.9) -> bool:
        """
        Validates whether the most recent substitution was within acceptable size bounds.

        This method compares the area of the substitute image (after being pasted into the source image)
        to the total area of the source image. If the substitute image covers too little or too much of
        the source (as defined by `threshold_min` and `threshold_max`), the substitution is considered invalid.

        Args:
            threshold_min (float, optional): The minimum acceptable ratio of substitute area to total image area.
                Defaults to 0.1 (10%). Values below this are considered too small to be valid.
            threshold_max (float, optional): The maximum acceptable ratio of substitute area to total image area.
                Defaults to 0.9 (90%). Values above this are considered too large and likely incorrect.

        Returns:
            bool: True if the substitution is within acceptable bounds, False otherwise.

        Notes:
            - This method requires that a substitution was previously performed using `substitute()`.
            - Ensure the internal state (e.g., placement position and size) is tracked for validation to work.
        """

        if not all([self.last_template, self.last_resized_substitute, self.last_placement_position]):
            raise ValueError("No substitution has been performed yet.")

        template_area = self.last_template.size[0] * self.last_template.size[1]
        substitute_area = self.last_resized_substitute.size[0] * self.last_resized_substitute.size[1]
        coverage_ratio = substitute_area / template_area

        if not (threshold_min <= coverage_ratio <= threshold_max):
            return False

        x, y = self.last_placement_position
        w, h = self.last_resized_substitute.size
        if x < 0 or y < 0 or x + w > self.last_template.size[0] or y + h > self.last_template.size[1]:
            return False

        return True

    def substitute_until_valid(
            self,
            source_img_path: str,
            substitute_img_path: str,
            cluster_range: tuple = (0, 10)
    ) -> Image.Image | None:
        """
        Attempts multiple substitutions using different dominant cluster amounts until a valid result is found.

        This method tries each value of `dominant_cluster_amount` within the specified `cluster_range`.
        The first substitution that passes validation (based on `validate_last_substitution`) is returned.

        Args:
            source_img_path (str): Path to the source image to modify.
            substitute_img_path (str): Path to the image to paste into the source.
            cluster_range (tuple, optional): A range of integers (inclusive) to use for dominant color clustering.
                Defaults to (0, 6). If 0 is used, white is used as the dominant color.

        Returns:
            PIL.Image.Image | None: The first successfully validated substituted image, or None if no valid
            configuration was found.

        Notes:
            - `cluster_range` should define a reasonable span to avoid unnecessary processing time.
        """

        for cluster_amount in range(cluster_range[0], cluster_range[1] + 1):
            result_img = self.substitute(
                source_img_path,
                substitute_img_path,
                dominant_cluster_amount=cluster_amount
            )

            if self.validate_last_substitution():
                return result_img

        return None
