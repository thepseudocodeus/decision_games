#!/bin/bash

# Enable not found global search to be an empty array
shopt -s nullglob

DIR="examples/playing-cards-png/Files/Cards_PNG"

if ! command -v convert &>/dev/null; then
    echo "Error: ImageMagick (convert) not installed"
    echo "Install with: brew install imagemagick  # Mac"
    echo "Or: sudo apt-get install imagemagick    # Ubuntu"
    exit 1
fi

if ! command -v potrace &>/dev/null; then
    echo "Error: potrace not installed"
    echo "Install with: brew install potrace  # Mac"
    echo "Or: sudo apt-get install potrace    # Ubuntu"
    exit 1
fi

# Does the directory exists?
if [ ! -d "$DIR" ]; then
    echo "Error: Directory $DIR does not exist or is not accessible."
    exit 1
fi

mkdir -p "${DIR}/../svg-cards/"

echo "we get here"

# Need to confirm we get png files
files=("$DIR"*.png)
if [ ${#files[@]} -eq 0 ]; then
    echo "Error: No .png files found in $DIR"
    exit 1
fi
echo "We find png files"

for file in "${files[@]}"; do
    echo "Working on: $file"
    if [ -f "$file" ]; then
        filename=$(basename "$file" .png)
        echo "Converting: $filename.png"

        # Note: must convert to bitmap first
        convert "$file" "${DIR}${filename}.pbm"
        potrace -s "${DIR}${filename}.pbm" -o "${DIR}/../svg-cards/${filename}.svg"

        rm -f "${DIR}${filename}.pbm"

        echo "  ✓ Created: ../svg-cards/${filename}.svg"
    fi
done

echo "Done! SVG files in: ${DIR}/../svg-cards/"
