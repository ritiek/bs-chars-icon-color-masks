# bs-chars-icon-color-masks

A python replicate using OpenCV to apply color texture masks on black & white base textures,
similar to how [Bombsquad game](http://bombsquadgame.com/) does it. The game files are not
distributed along with this tool, you need to download them separately from
https://files.ballistica.net/bombsquad/builds/.


## Installation

```bash
$ git clone https://github.com/ritiek/bs-chars-icon-color-masks
$ cd bs-chars-icons-color-masks/
$ pip install -r requirements.txt
```

## Usage

The program can be used either as a standalone webserver or imported as a python module.

### Standalone webserver

Running
```bash
$ python bs_icon_masks.py
Usage: python bs_icon_masks.py <path/to/bombsquad/textures/directory> <webserver-port>
```
should display a similar usage help message.

For example, try running
```bash
$ python bs_icon_masks.py ~/bombsquad/ba_data/textures/ 8000
```
and open this in your browser:
http://0.0.0.0:8000/?icon=neoSpazIcon&mask=neoSpazIconColorMask&main=(1.0,0.3,0.0)&highlight=(0.5,0.2,0.8)

Try messing with the parameters and see how that affects the image.

### Python module

```python
from bs_icon_masks import ApplyColorMask
import os

bs_textures_dir = "/path/to/bombsquad/ba_data/textures/"

icon = os.path.join(bs_textures_dir, "neoSpazIcon.dds")
mask = os.path.join(bs_textures_dir, "neoSpazIconColorMask.dds")
main_color = (1.0, 0.3, 0.0)
highlight_color = (0.5, 0.2, 0.8)

spaz = ApplyColorMask(icon, mask, main_color, highlight_color)
# Returns a cv2 image object
color_spaz = spaz.apply_transformation()

import cv2
# Display transformed spaz
cv2.imshow("Transformed Spaz", color_spaz/255.0)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save transformed spaz on disk
cv2.imwrite("transformed_spaz.png", color_spaz)
```
