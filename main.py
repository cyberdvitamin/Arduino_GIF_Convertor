import os, sys
from tkinter import Tk, Label, Button, Entry, filedialog, StringVar, OptionMenu
from PIL import Image, ImageSequence


def get_output_dir():
    if getattr(sys, 'frozen', False):
        # PyInstaller adds this attribute when the script is running as an executable
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    output_dir = os.path.join(base_path, "display_gif")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def convert_gif_to_frames(gif_path, frame_delay, angle):
    print(f"Converting GIF: {gif_path} with frame delay: {frame_delay} and rotation angle: {angle}")
    frames = []
    with Image.open(gif_path) as img:
        for frame in ImageSequence.Iterator(img):
            frame = frame.copy().rotate(angle, expand=True).resize((128, 64)).convert('1')
            if not is_empty_frame(frame):
                frames.append(frame)
    if not frames:
        raise ValueError("No valid frames found in the GIF.")
    return frames, frame_delay


def convert_image_to_frame(image_path, angle):
    print(f"Converting image: {image_path} with rotation angle: {angle}")
    with Image.open(image_path) as img:
        frame = img.rotate(angle, expand=True).resize((128, 64)).convert('1')
    if is_empty_frame(frame):
        raise ValueError("The image frame is empty.")
    return [frame]


def is_empty_frame(frame):
    return frame.getbbox() is None


def image_to_byte_array(img):
    byte_array = img.tobytes()
    if len(byte_array) != 1024:
        raise ValueError("Frame size is incorrect!")
    return byte_array


def generate_header(frames, frame_delay, start, output_file):
    print(f"Generating header file: {output_file}")
    with open(output_file, 'w') as f:
        f.write('#ifndef FRAMES_H\n')
        f.write('#define FRAMES_H\n\n')
        f.write('#include <pgmspace.h>\n\n')
        f.write(f'#define NUM_FRAMES {len(frames)}\n')
        f.write(f'#define FRAME_DELAY {frame_delay}\n')
        f.write(f'#define START {start}\n\n')
        f.write('const unsigned char PROGMEM frames[][1024] = {\n')

        for i, frame in enumerate(frames):
            byte_array = image_to_byte_array(frame)
            f.write('  {')
            f.write(','.join(f'0x{byte:02x}' for byte in byte_array))
            f.write('}')
            if i < len(frames) - 1:
                f.write(',\n')

        f.write('\n};\n\n')
        f.write('#endif // FRAMES_H\n')
    print(f"Header file generated successfully at {output_file}")


def main():
    def browse_files():
        file_path = filedialog.askopenfilename(
            filetypes=[("GIF files", "*.gif"), ("Image files", "*.png;*.jpg;*.jpeg")]
        )
        file_path_entry.delete(0, "end")
        file_path_entry.insert(0, file_path)

        if file_path.lower().endswith('.gif'):
            try:
                with Image.open(file_path) as img:
                    num_frames = sum(1 for _ in ImageSequence.Iterator(img))
                frame_count_label.config(text=f"Number of frames: {num_frames}")
                # Recommend frame delay based on a frame rate of 24 FPS
                recommended_delay = int(1000 / 24)
                delay_entry.delete(0, "end")
                delay_entry.insert(0, str(recommended_delay))
                recommendation_label.config(text=f"Recommended frame delay: {recommended_delay} ms")
            except Exception as e:
                frame_count_label.config(text=f"Error reading GIF: {e}")
        else:
            frame_count_label.config(text="Number of frames: 1")
            recommendation_label.config(text="")

    def convert():
        file_path = file_path_entry.get()
        if not file_path:
            result_label.config(text="No file selected!")
            return

        frame_delay = delay_entry.get()
        if not frame_delay.isdigit():
            result_label.config(text="Invalid frame delay! Please enter a number.")
            return

        frame_delay = int(frame_delay)
        angle = int(rotation_var.get())

        try:
            if file_path.lower().endswith('.gif'):
                frames, frame_delay = convert_gif_to_frames(file_path, frame_delay, angle)
                num_frames = len(frames)
                start = 1
            else:
                frames = convert_image_to_frame(file_path, angle)
                frame_delay = 0  # Static images do not need a frame delay
                num_frames = 1
                start = 0

            # Ensure the output directory exists
            output_dir = get_output_dir()
            #os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, 'frames.h')

            generate_header(frames, frame_delay, start, output_file)
            result_label.config(
                text=f"Conversion complete. {num_frames} frame(s) generated. Header file created at {output_file}.")
            print(f"{num_frames} frame(s) generated.")
        except ValueError as e:
            result_label.config(text=f"Error: {e}")
            print(f"Error: {e}")

    # Create the main window
    root = Tk()
    root.title("GIF/Image to Arduino Header Converter")

    # Add widgets
    Label(root, text="Select GIF or Image file:").grid(row=0, column=0, padx=10, pady=10)
    file_path_entry = Entry(root, width=50)
    file_path_entry.grid(row=0, column=1, padx=10, pady=10)
    Button(root, text="Browse", command=browse_files).grid(row=0, column=2, padx=10, pady=10)

    frame_count_label = Label(root, text="")
    frame_count_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    Label(root, text="Frame delay (ms, only for GIFs):").grid(row=2, column=0, padx=10, pady=10)
    delay_entry = Entry(root, width=10)
    delay_entry.grid(row=2, column=1, padx=10, pady=10)
    delay_entry.insert(0, "100")  # Default delay for GIFs

    recommendation_label = Label(root, text="")
    recommendation_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    Label(root, text="Rotation angle:").grid(row=4, column=0, padx=10, pady=10)
    rotation_var = StringVar(root)
    rotation_var.set("0")  # default value
    rotation_menu = OptionMenu(root, rotation_var, "0", "90", "180", "270")
    rotation_menu.grid(row=4, column=1, padx=10, pady=10)

    Button(root, text="Convert", command=convert).grid(row=5, column=1, padx=10, pady=20)

    result_label = Label(root, text="")
    result_label.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    # Run the GUI main loop
    root.mainloop()


if __name__ == '__main__':
    main()
