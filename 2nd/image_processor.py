import cv2
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
import os


def classify_object(brightness, size):
    if size < 4 and brightness < 60:
        return "звезда"
    elif size >= 4 and size < 9 and brightness < 200 and brightness >= 60:
        return "галактика"
    elif size >= 9:
        return "суперновая"
    else:
        return "неизвестно"


COLORS = {
    'звезда': (255, 0, 0),
    'галактика': (0, 0, 255),
    'суперновая': (0, 255, 0)
}


def process_image_section(image_section, offset_x, offset_y):
    edges = cv2.Canny(image_section, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    object_stats = []
    for contour in contours:
        area = cv2.contourArea(contour)

        (x, y), radius = cv2.minEnclosingCircle(contour)
        center = (int(x) + offset_x, int(y) + offset_y)
        radius = int(radius)

        mask = np.zeros_like(image_section)
        cv2.circle(mask, (int(x), int(y)), radius, 255, -1)
        object_pixels = image_section[mask == 255]

        brightness = np.mean(object_pixels)
        classification = classify_object(brightness, area)

        object_stats.append({
            'center_x': center[0],
            'center_y': center[1],
            'radius': radius,
            'brightness': brightness,
            'size': area,
            'classification': classification
        })

    return object_stats


def draw_circles(full_image, object_stats):
    for obj in object_stats:
        classification = obj['classification']
        center = (obj['center_x'], obj['center_y'])
        radius = obj['radius']

        if classification in COLORS:
            color = COLORS[classification]
            cv2.circle(full_image, center, radius, color, 2)


def process_image(image_path, output_folder):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    orig_image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    if image is None:
        print(f"Ошибка: Не удалось загрузить изображение {image_path}")
        return []

    height, width = image.shape

    quadrants = [
        (image[0:height // 2, 0:width // 2], 0, 0),
        (image[0:height // 2, width // 2:width], width // 2, 0),
        (image[height // 2:height, 0:width // 2], 0, height // 2),
        (image[height // 2:height, width // 2:width], width // 2, height // 2)
    ]

    all_object_stats = []
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(process_image_quadrant, quadrants)

    for quadrant_stats in results:
        all_object_stats.extend(quadrant_stats)

    draw_circles(orig_image, all_object_stats)

    output_image_path = os.path.join(output_folder, os.path.basename(image_path))
    cv2.imwrite(output_image_path, orig_image)

    return all_object_stats


def process_image_quadrant(quadrants):
    image_section, offset_x, offset_y = quadrants
    return process_image_section(image_section, offset_x, offset_y)


def parallel_process_images(image_paths, output_folder, num_workers=16):
    all_images_stats = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = executor.map(process_image, image_paths, [output_folder] * len(image_paths))

    for image_stats in results:
        all_images_stats.extend(image_stats)

    return pd.DataFrame(all_images_stats)
