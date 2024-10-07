# System and basic packages
import sys
import os
import re
import struct
import yaml

# Image and array manipulation
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


# # # Utility Functions
def extract_number(filename: str) -> int:
    """Extracts the number from the filename."""
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else -1

def sort_filenames_by_number(filenames: list[str]) -> list[str]:
    """Sorts a list of filenames by the number contained in the name."""
    return sorted(filenames, key=extract_number)

def print_loading_bar(counter: int, total: int, previous_message: str = 'Processing') -> None:
    """Prints a loading bar with colors that updates in place."""
    bar_length = 40
    progress = counter / total
    block = int(round(bar_length * progress))
    bar = f"\033[92m{'█' * block}\033[0m{'-' * (bar_length - block)}"
    sys.stdout.write(f"\r{previous_message}: [{bar}] {counter}/{total} ({int(progress * 100)}%)")
    sys.stdout.flush()

def count_total_elements(data: int | list | dict) -> int:
    """Counts the total number of elements in a nested structure."""
    if isinstance(data, dict):
        return sum(count_total_elements(value) for value in data.values())
    elif isinstance(data, list):
        return sum(count_total_elements(item) for item in data)
    else:
        return 1

def load_config(config_path: str) -> dict:
    """Loads configuration from a YAML file."""
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    return config


# # # Processing Functions
def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalizes a float32 image to the range [0, 255]."""
    image = image + np.min(image) * -1
    image = image / np.max(image) * 255
    return np.clip(image, 0, 255)

def calculate_average_slices(images: list[np.ndarray], n_slices_average: int) -> list[np.ndarray]:
    """Calculates the average of images in groups of n_slices_average."""
    assert len(images) % n_slices_average == 0, f"Error: Number of images ({len(images)}) is not divisible by n_slices_average ({n_slices_average})."
    n_groups = len(images) // n_slices_average
    return [np.mean(images[i * n_slices_average:(i + 1) * n_slices_average], axis=0) for i in range(n_groups)]

def load_and_preprocess_images(folder: str, n_slices_in_volume: int, cycle_of_repeated_bscan: int, image_size: tuple, normalize_individual: bool) -> dict:
    """Loads and preprocesses images from the folder."""
    files = os.listdir(folder)
    files = sort_filenames_by_number(files)
    # files = [x for x in files if int(x.replace('.raw', '').replace('Bscan_', '')) >= 5000] # JUST FOR TRY

    processed_volume_slices = {}
    for counter, filename in enumerate(files):
        print_loading_bar(counter, len(files), 'Reading images')

        # Determine current volume and slice
        if counter % n_slices_in_volume == 0:
            id_volume = int(counter / n_slices_in_volume)
            processed_volume_slices[id_volume] = {}

        id_slice = int(counter % cycle_of_repeated_bscan)
        if id_slice not in processed_volume_slices[id_volume]:
            processed_volume_slices[id_volume][id_slice] = []

        # Read and convert binary data
        file_path = os.path.join(folder, filename)
        with open(file_path, 'rb') as file:
            raw_data = file.read()

        num_bytes = len(raw_data)
        num_floats = num_bytes // 4
        float_array = np.array(struct.unpack('<' + 'f' * num_floats, raw_data), dtype=np.float32)

        assert len(float_array) == image_size[0] * image_size[1], f"Error: float_array len ({len(float_array)}) must be equal to image_size - Height x Width ({image_size[0] * image_size[1]})"

        image = float_array.reshape(image_size)
        image = image[:, 10:]
        image = np.rot90(image, k=3)

        if normalize_individual:
            image = normalize_image(image)

        processed_volume_slices[id_volume][id_slice].append(image)

    print_loading_bar(len(files), len(files), 'Reading images')  # Final update
    print('\n')
    return processed_volume_slices

def filter_and_average_slices(processed_volume_slices: dict, cycle_of_repeated_bscan: int, n_primary_slices: int, post_processing_average_per_n_slices: int, normalize_postprocessed: bool, save_folder: str, save_image: bool):
    """Filters, averages, and saves slices."""
    volumes_to_remove = [id_volume for id_volume in processed_volume_slices if len(processed_volume_slices[id_volume][cycle_of_repeated_bscan - 1]) != n_primary_slices]
    for id_volume in volumes_to_remove:
        print(f"Deleting volume: {id_volume} - {id_volume * 500} because it doesn't have the required number of slices")
        del processed_volume_slices[id_volume]

    n_total_elements = int(count_total_elements(processed_volume_slices) / post_processing_average_per_n_slices)
    counter_ele = 0
    for id_volume in processed_volume_slices:
        for id_slice in processed_volume_slices[id_volume]:
            if post_processing_average_per_n_slices > 1:
                processed_volume_slices[id_volume][id_slice] = calculate_average_slices(
                    processed_volume_slices[id_volume][id_slice], post_processing_average_per_n_slices
                )

            for counter, average_image in enumerate(processed_volume_slices[id_volume][id_slice]):
                print_loading_bar(counter_ele, n_total_elements)
                counter_ele += 1
                if normalize_postprocessed:
                    average_image = normalize_image(average_image)
                average_image = average_image.astype(np.uint8)

                out_filename = f"{id_slice}_{counter}.png"
                if save_image:
                    image = Image.fromarray(average_image)
                    save_path = os.path.join(save_folder, f"{id_volume}", out_filename)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    image.save(save_path)
                else:
                    plt.imshow(average_image, cmap='gray')
                    plt.colorbar()
                    plt.title(f"Image {id_volume}_{out_filename}")
                    plt.show()
    
    # Last iteraction
    print_loading_bar(counter_ele, n_total_elements)



if __name__ == "__main__":
    # Load configuration
    config = load_config('config.yaml')

    # Config Variables
    folder = config['folder']
    save_folder = config['save_folder']
    n_slices_in_volume = config['n_slices_in_volume']
    cycle_of_repeated_bscan = config['cycle_of_repeated_bscan']
    image_size = tuple(config['image_size'])
    post_processing_average_per_n_slices = config['post_processing_average_per_n_slices']
    normalize_individual_image = config['normalize_individual_image']
    normalize_postprocessed_images = config['normalize_postprocessed_images']
    save_image = config['save_image']

    # Check input validity
    n_primary_slices = int(n_slices_in_volume / cycle_of_repeated_bscan)
    assert n_slices_in_volume % cycle_of_repeated_bscan == 0, f"Error: n_slices_in_volume ({n_slices_in_volume}) must be divisible by cycle_of_repeated_bscan ({cycle_of_repeated_bscan})"
    assert n_primary_slices % post_processing_average_per_n_slices == 0, f"Error: Number of images per slice ({n_primary_slices}) must be divisible by post_processing_average_per_n_slices ({post_processing_average_per_n_slices})"

    # Load and preprocess images
    processed_volume_slices = load_and_preprocess_images(folder, n_slices_in_volume, cycle_of_repeated_bscan, image_size, normalize_individual_image)

    # Filter and average slices, then save or display images
    filter_and_average_slices(processed_volume_slices, cycle_of_repeated_bscan, n_primary_slices, post_processing_average_per_n_slices, normalize_postprocessed_images, save_folder, save_image)