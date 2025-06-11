# rememepy
Rememepy is a simple tool to help you replace main images in memes.
```python
from rememepy import Generator
from PIL import Image

gen = Generator()
meme = gen.substitute("meme.jpg", "substitute.jpg")
meme.show()
```

## Features
### `substitute()` Function
The image substitution algorithm uses several adjustable parameters and returns a `PIL.Image.Image` object.

```python
def substitute(
    source_img_path: str,
    substitute_img_path: str,
    dominant_cluster_amount: int = 3,
    resize_to: tuple | None = None
) -> PIL.Image.Image
```
- `dominant_cluster_amount`: Controls the number of color clusters used to determine the dominant color in the image. Increasing this value can help identify the main image more precisely. If set to `0`, the dominant color is assumed to be white.
- `resize_to`: Optionally resizes the substitute image to the specified dimensions. If `None`, the substitute will be stretched to cover the target area.

### Validating Substitution Results
Some memes may cover the entire image area or contain multiple images, which can make substitution less accurate. To check whether the substitution was successful, call `validate_last_substitution()` after `substitute(...)`.
```python
def validate_last_substitution(
    threshold_min: float = 0.1,
    threshold_max: float = 0.9
) -> bool
```
- `threshold_min`: The minimum portion of the image the substitute should cover.
- `threshold_max`: The maximum portion of the image the substitute is allowed to cover.

### Foolproof Substitution
The `substitute_until_valid()` method automatically tries different combinations of parameters until a valid substitution is found or all options have been exhausted. If no valid result is found, it returns `None`.
```python
def substitute_until_valid(
    source_img_path: str,
    substitute_img_path: str,
    cluster_range: tuple = (0, 6)
) -> PIL.Image.Image | None
```
- `cluster_range`: A range of values for `dominant_cluster_amount` to try. A wider range increases the likelihood of success but also takes more time.

## Installing Rememepy and Supported Versions
Rememepy is available on [PyPi](https://pypi.org/project/rememepy/):
```console
$ python -m pip install rememepy
```
Rememepy officially supports Python XX.
