from PIL import Image

def cut_image(input_path, output_prefix, coordinates):
    # Open the PNG file
    original_image = Image.open(input_path)

    # Ensure the image mode is RGBA for proper handling of PNG with transparency
    if original_image.mode != 'RGBA':
        original_image = original_image.convert('RGBA')

    # Get image dimensions
    width, height = original_image.size

    # Iterate through the y-coordinates in the tuple
    for index, (y1, y2) in enumerate(coordinates):
        # Ensure y2 is not greater than the image height
        y2 = min(y2, height)

        # Crop the image based on y1 and y2
        cropped_image = original_image.crop((0, y1, width, y2))

        # Save the cropped image
        output_path = f"{output_prefix}_{index + 1}.png"
        cropped_image.save(output_path)

if __name__ == "__main__":
    # Example usage
    input_image_path = "nikita-linked-profile.v2.png"
    output_prefix = "nikita-profile-part"
    y_coordinates = [
        (0, 820), 
        (820, 1545),
        (1914, 2830),
        (2835, 4055),
        (4055, 4587),
        (4587, 6730),
        (6730, 7678),
(7678,8371),
(8371,9151),
(9151,10345),
(10345,11325),
(11325,12323),
(12323,12730),
(12730,12958)

        ]  # Adjust as needed

    cut_image(input_image_path, output_prefix, y_coordinates)
