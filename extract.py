import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

# --- CONFIGURATION ---
OUTPUT_FILE = "INDEX_DETAILED.md"

# The "Standard" Windows XP Map (with Shift logic applied later)
XP_DESCRIPTIONS = {
    1: "Default Document",
    2: "Executable Application",
    3: "Closed Folder",
    4: "Open Folder",
    5: "5.25 Floppy Disk",
    6: "3.5 Floppy Disk",
    7: "Removable Drive",
    8: "Hard Disk Drive",
    9: "Network Drive (Connected)",
    10: "Network Drive (Disconnected)",
    11: "CD-ROM Drive",
    12: "RAM Chip",
    13: "Entire Network (Globe)",
    14: "Network Computer",
    15: "My Computer",
    16: "Server",
    17: "Printer",
    18: "Network Printer",
    19: "Paint Image",
    20: "History / Time",
    21: "Recycle Bin (Mixed)",
    22: "Help Book",
    23: "Search (Magnifying Glass)",
    24: "Information (Blue i)",
    25: "Shutdown Button",
    26: "Sharing Hand",
    27: "Sharing Hand (Variant)",
    28: "User Accounts",
    29: "Shortcut Arrow",
    31: "Recycle Bin (Empty)",
    32: "Recycle Bin (Full)",
    33: "Dial-up Networking",
    34: "Show Desktop",
    35: "Control Panel",
    36: "Program Group",
    37: "Printers Folder",
    38: "Fonts Folder",
    39: "Windows Flag",
    40: "Audio CD",
    41: "Tree Structure",
    42: "Multiple Documents",
    43: "Favorites Star",
    44: "Find Document",
    45: "Help Temp",
    137: "Run Dialog",
    149: "My Documents",
    210: "Folder (Pictures)",
    220: "Folder (Music)",
    235: "My Music",
    236: "My Pictures",
    237: "My Videos",
    290: "Security Shield",
}

def analyze_folder_contents(folder_path):
    """
    Returns a tuple: (best_image_filename, file_count, size_summary)
    It tries to find the highest resolution and highest bit-depth image.
    """
    files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
    if not files:
        return None, 0, "Empty"

    # Regex to parse filenames like "rawid_32x32_32bit.png" or "rawid_32px.png"
    # We want to score images to find the "Hero" image.
    best_score = -1
    best_file = files[0]
    
    sizes_found = set()

    for f in files:
        # Score calculation: Width * 100 + Bits
        score = 0
        width = 0
        bits = 0
        
        # Extract numbers
        nums = list(map(int, re.findall(r'\d+', f)))
        
        # Guessing format based on numbers found
        if len(nums) >= 4: # e.g. 6_48x48_32bit
            width = nums[1]
            bits = nums[3]
        elif len(nums) >= 2: # e.g. 6_48px
            width = nums[1]
            bits = 8 # Assume 8-bit if not specified
        
        sizes_found.add(f"{width}px")
        
        # Weight larger sizes heavily, then bit depth
        score = (width * 1000) + bits
        
        if score > best_score:
            best_score = score
            best_file = f

    # Create a nice summary string (e.g., "16px, 32px, 48px")
    # Sort sizes numerically
    sorted_sizes = sorted(list(sizes_found), key=lambda x: int(x.replace('px','')))
    size_summary = ", ".join(sorted_sizes)

    return best_file, len(files), size_summary

def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select your 'Sorted_Icons' folder")
    return folder_selected

def generate_index():
    source_folder = select_folder()
    
    if not source_folder:
        return

    parent_dir = os.path.dirname(source_folder)
    output_path = os.path.join(parent_dir, OUTPUT_FILE)

    try:
        folders = [f for f in os.listdir(source_folder) if os.path.isdir(os.path.join(source_folder, f))]
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return
    
    # Sort naturally
    def get_id(name):
        match = re.search(r'\d+', name)
        return int(match.group()) if match else 99999
    
    folders.sort(key=get_id)

    print(f"Generating detailed index from '{source_folder}'...")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Windows XP Icon Index (Detailed)\n\n")
        f.write(f"**Source Folder:** `{os.path.basename(source_folder)}`\n\n")
        f.write("This index accounts for the **+1 Shift** in IDs and lists all available sizes.\n\n")
        
        # Table Header
        f.write("| ID | Preview | Variants | Sizes Found | Identity |\n")
        f.write("| :---: | :---: | :---: | :--- | :--- |\n")

        for folder_name in folders:
            folder_id = get_id(folder_name)
            folder_full_path = os.path.join(source_folder, folder_name)
            
            # 1. Analyze Contents (Find Hero Image & Stats)
            hero_image, count, size_summary = analyze_folder_contents(folder_full_path)
            
            # 2. Shift Logic for Description
            desc = "Unknown"
            if folder_id == 1: desc = "**Default Document**"
            elif folder_id == 2: desc = "**Default Document (Duplicate)**"
            elif folder_id > 2:
                shifted_id = folder_id - 1
                desc = XP_DESCRIPTIONS.get(shifted_id, f"Icon {shifted_id}")

            # 3. Format Image Link
            if hero_image:
                base_folder_name = os.path.basename(source_folder)
                rel_path = f"{base_folder_name}/{folder_name}/{hero_image}".replace("\\", "/").replace(" ", "%20")
                preview_md = f"![{folder_id}]({rel_path})"
            else:
                preview_md = "-"

            # 4. Write Row
            f.write(f"| **{folder_id}** | {preview_md} | {count} Files | {size_summary} | {desc} |\n")

    messagebox.showinfo("Success", f"Detailed Index Created!\n\nLocation: {output_path}")

if __name__ == "__main__":
    generate_index()