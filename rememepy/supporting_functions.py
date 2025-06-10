from PIL import Image
import numpy as np
import scipy
import scipy.cluster


def find_dominant_color(img: Image, dominant_clusters_amount: int, resize: tuple | None = None) -> tuple:
    """Finds the color that covers most of the image."""

    # the option to resize the image
    img = img.resize(resize) if resize is not None else img

    ar = np.asarray(img)
    shape = ar.shape
    ar = ar.reshape(np.prod(shape[:2]), shape[2]).astype(float)

    codes, dist = scipy.cluster.vq.kmeans(ar, dominant_clusters_amount)

    vecs, dist = scipy.cluster.vq.vq(ar, codes)  # assign codes
    counts, bins = np.histogram(vecs, len(codes))  # count occurrences

    index_max = np.argmax(counts)  # find most frequent
    peak = codes[index_max]

    return tuple(peak)


def are_colors_similar(color1: tuple, color2: tuple, tolerance: int) -> bool:
    """Compares if two colors are similar enough."""

    color1_sum = color1[0] + color1[1] + color1[2]
    color2_sum = color2[0] + color2[1] + color2[2]
    difference = abs(color2_sum - color1_sum)
    if difference < tolerance:
        return True
    else:
        return False


def find_placement(template: Image, dominant_color: tuple) -> tuple:
    """Finds the ideal area for a substitute image to be pasted to."""

    template_width, template_height = template.size
    template_pixel_grid = template.load()

    substitute_width, substitute_height = 0, 0
    starting_position = None
    current_matching_lines_streak = 0

    # runs through every line of pixels in the image to find which lines are mostly not made up of the dominant color
    for y in range(template_height):
        tolerance = template_width // 2  # set tolerance for how many dominant color pixels are allowed per line
        line_start = None
        last_different = None
        passed = True

        # running through one line
        for x in range(template_width):
            try:
                color = template_pixel_grid[x, y]  # get the color of the current pixel
            except IndexError:
                raise f"Error with extracting pixel colors pos {x}/{y}"
            else:
                # check if the color is similar to the dominant color
                if are_colors_similar(color, dominant_color, 30):
                    tolerance -= 1  # decrease tolerance if pixel matches dominant color
                    if tolerance == 0:
                        passed = False  # too many dominant color pixels, line fails
                        break

                    # update substitute width if a longer segment is found
                    if line_start is not None and last_different is not None:
                        current_line_length = last_different[0] - line_start[0]
                        if current_line_length > substitute_width:
                            substitute_width = current_line_length

                else:
                    last_different = x, y  # update last different color pixel
                    if line_start is None:
                        line_start = x, y  # mark start of different color segment

            # update substitute width if a longer segment is found
            if line_start is not None and last_different is not None:
                current_line_length = last_different[0] - line_start[0]
                if current_line_length > substitute_width:
                    substitute_width = current_line_length

        # if the line passed, increment streak of matching lines
        if passed and y != template_height - 1:
            current_matching_lines_streak += 1
        else:
            # update substitute height and starting position if a larger area is found
            if substitute_height < current_matching_lines_streak and line_start is not None:
                substitute_height = current_matching_lines_streak
                starting_position = line_start[0], line_start[1] - substitute_height
            current_matching_lines_streak = 0

    return starting_position, (substitute_width, substitute_height)
