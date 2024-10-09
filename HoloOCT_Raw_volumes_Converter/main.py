# System and basic packages
import sys
import os
import struct
import yaml
import re

# Array and image manipulation packages
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2


# Utility Functions
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



# Processing Functions
def normalize_image_float32(image: np.ndarray) -> np.ndarray:
    """Normalizes a float32 image to the range [0, 255]."""
    image = image + np.min(image) * -1
    image = image / np.max(image) * 255
    return np.clip(image, 0, 255)

def normalize_image_complex64(image: np.ndarray) -> np.ndarray:
    """Normalizes a complex64 image to the range [0, 255]."""
    image = (255 * (image / np.max(image)))
    return image

def calculate_average_slices(images: list[np.ndarray], n_slices_average: int) -> list[np.ndarray]:
    """Calculates the average of images in groups of n_slices_average."""
    assert len(images) % n_slices_average == 0, f"Error: Number of images ({len(images)}) is not divisible by n_slices_average ({n_slices_average})."
    n_groups = len(images) // n_slices_average
    return [np.mean(images[i * n_slices_average:(i + 1) * n_slices_average], axis=0) for i in range(n_groups)]

def linear_histogram_stretching(image, lower_percentile=1, upper_percentile=99):
    """Aply lineal stretching using percentils to improve the image contrast"""
    lower_bound = np.percentile(image, lower_percentile)
    upper_bound = np.percentile(image, upper_percentile)
    
    # Clip and scale the image
    stretched_image = np.clip((image - lower_bound) / (upper_bound - lower_bound), 0, 1)
    stretched_image = (stretched_image * 255).astype(np.uint8)
    
    return stretched_image

def register_images(reference_image: np.ndarray, image_list: list[np.ndarray]):
    """Registers a list of images with respect to a reference image using the ECC algorithm.

    Args:
        reference_image (np.ndarray): The reference image.
        image_list (List[np.ndarray]): List of images to register.

    Returns:
        List[np.ndarray]: List of registered images.
    """
    registered_images = []
    sz = reference_image.shape
    warp_mode = cv2.MOTION_AFFINE # You can try cv2.MOTION_TRANSLATION, cv2.MOTION_EUCLIDEAN or cv2.MOTION_AFFINE

    # Define the initial warp matrix
    warp_matrix = np.eye(2, 3, dtype=np.float32)

    # Termination criteria
    number_of_iterations = 500
    termination_eps = 1e-6
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations, termination_eps)

    # Convert reference image to float32 and register
    im1_gray = reference_image.astype(np.float32)
    registered_images.append(im1_gray)
    for image in image_list:
        # Convert images to float32 if necessary
        im2_gray = image.astype(np.float32)

        # Perform the ECC algorithm
        try:
            _, warp_matrix = cv2.findTransformECC(im1_gray, im2_gray, warp_matrix, warp_mode, criteria)
            # Apply the warp transformation to the image
            im2_aligned = cv2.warpAffine(im2_gray, warp_matrix, (sz[1], sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
            registered_images.append(im2_aligned)
        except cv2.error as e:
            print(f"Error during image registration: {e}")
            # If registration fails, add the original image
            registered_images.append(im2_gray)

    return registered_images


# Processing large individual files
def read_large_file_in_batches(filepath: str, data_format: str, width: int, height: int, num_bscans: int, batch_size: int, normalize_func, normalize_individual: bool):
    """Reads a large file in batches to avoid memory overload."""
    bytes_per_value = 8 if 'complex64' in data_format else 4

    # Open file by sections
    with open(filepath, 'rb') as file:
        for bscan_idx in range(0, num_bscans, batch_size):
            bscans = []
            for i in range(batch_size):
                if bscan_idx + i >= num_bscans:
                    break

                # Read data
                raw_data = file.read(bytes_per_value * width * height)
                if data_format == 'complex64':
                    float_array = np.frombuffer(raw_data, dtype=np.complex64)
                    float_array = np.abs(float_array)
                else:
                    float_array = np.frombuffer(raw_data, dtype=np.float32)

                # Reshape and rotate
                bscan_image = float_array.reshape((width, height))
                bscan_image = np.rot90(bscan_image, k=3)
                if normalize_individual:
                    bscan_image = normalize_func(bscan_image)
                bscans.append(bscan_image)

            yield bscans  # Return the batch of B-scans

def process_large_files_in_folder(folder: str, n_slices_in_volume: int, post_processing_average_per_n_slices: int, image_size: tuple, data_format: str, normalize_individual: bool, normalize_postprocessed: bool, normalize_func, post_processing_dic: dict, save_folder: str, save_image: bool):
    """Processes all large files in the folder containing multiple B-scans."""
    files = [f for f in os.listdir(folder) if f.endswith('.raw')]
    total_files = len(files)
    width, height = image_size
    if post_processing_dic['clahe'] == True:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    # Process files in folder
    for file_idx, filename in enumerate(files):
        print(f"Processing file {file_idx + 1}/{total_files}: {filename}")
        filepath = os.path.join(folder, filename)

        # Process the large file in batches
        total_batches = n_slices_in_volume // post_processing_average_per_n_slices
        print_loading_bar(0, total_batches, previous_message=f'Processing batches in file {file_idx + 1}/{total_files}')
        for batch_idx, bscan_batch in enumerate(read_large_file_in_batches(filepath, data_format, width, height, n_slices_in_volume, post_processing_average_per_n_slices, normalize_func, normalize_individual)):
            # Average the batch
            if post_processing_average_per_n_slices > 1:
                if post_processing_dic['register_images_pre_average'] == True: # Register images
                    bscan_batch = register_images(bscan_batch[0], bscan_batch)
                averaged_bscan = np.mean(bscan_batch, axis=0)
            else:
                averaged_bscan = np.array(bscan_batch)[0]
            
            # Normalize averaged images
            if normalize_postprocessed:
                averaged_bscan = normalize_func(averaged_bscan)
            averaged_bscan = averaged_bscan.astype(np.uint8)

            # Postprocess final image if necessary
            if post_processing_dic['clahe'] == True:
                averaged_bscan = clahe.apply(averaged_bscan)

            # Save or display the image
            out_filename = f"bscan_{file_idx}_{batch_idx}.png"
            if save_image:
                image = Image.fromarray(averaged_bscan)
                save_path = os.path.join(save_folder, out_filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                image.save(save_path)
            else:
                plt.imshow(averaged_bscan, cmap='gray')
                plt.colorbar()
                plt.title(f"B-scan {file_idx}_{batch_idx}")
                plt.show()

            # Print the progress bar for batches
            print_loading_bar(batch_idx + 1, total_batches, previous_message=f'Processing batches in file {file_idx + 1}/{total_files}')


# Processing individual files (OLD FORMAT)
def load_and_preprocess_images(folder: str, n_slices_in_volume: int, cycle_of_repeated_bscan: int, image_size: tuple, normalize_individual: bool, normalize_func) -> dict:
    """Loads and preprocesses images from the folder."""
    files = os.listdir(folder)
    files = sort_filenames_by_number(files)
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
            image = normalize_func(image)

        processed_volume_slices[id_volume][id_slice].append(image)

    print_loading_bar(len(files), len(files), 'Reading images')  # Final update
    print('\n')
    return processed_volume_slices

def filter_and_average_slices(processed_volume_slices: dict, cycle_of_repeated_bscan: int, n_primary_slices: int, post_processing_average_per_n_slices: int, normalize_postprocessed: bool, normalize_func, save_folder: str, save_image: bool):
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
                    average_image = normalize_func(average_image)
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
    multiple_files_per_file = config.get('multiple_files_per_file', False)
    data_format = config.get('data_format', 'float32')
    post_processing_dic = config['post_process_image']

    # Select normalization function based on data_format
    if data_format == 'complex64':
        normalize_func = normalize_image_complex64
    else:
        normalize_func = normalize_image_float32

    # Process files
    if multiple_files_per_file:
        process_large_files_in_folder(folder, n_slices_in_volume, post_processing_average_per_n_slices, image_size, data_format, normalize_individual_image, normalize_postprocessed_images, normalize_func, post_processing_dic, save_folder, save_image)
    else:
        # Load and preprocess images in standard format
        processed_volume_slices = load_and_preprocess_images(folder, n_slices_in_volume, cycle_of_repeated_bscan, image_size, normalize_individual_image, normalize_func)

        # Filter and average slices, then save or display images
        filter_and_average_slices(processed_volume_slices, cycle_of_repeated_bscan, n_slices_in_volume // cycle_of_repeated_bscan, post_processing_average_per_n_slices, normalize_postprocessed_images, normalize_func, save_folder, save_image)
