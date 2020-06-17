# Exploring the options for a Raspberry PI alternative setup

The existing ODM 360 leverages the Sony α6000 and gphoto2 for control. This has advantages: the primary being that the α6000 is a very nice camera with excellent available optics and chipset. The disadvantages are cost, weight, and freedom. By freedom we mean that the camera itself is not free or open source.

![](https://www.raspberrypi.org/homepage-9df4b/static/f71633ede5f3881b071d5c7539a5b1f4/f8408/03b5b033-5aca-40a7-ae4a-1592a9403890_CAM%2BHERO%2BALT%2B2.jpg)

Using the [Raspberry Pi High Quality Camera](https://www.raspberrypi.org/products/raspberry-pi-high-quality-camera/) may be an affordable alternative that could give good results and be free and open source in it's full implementation. The chipset and optics are likely to be quite adequate for the purposes, so let's step through the logistics and cost. One caveat is that the Pi High Quality camera is built around a video camera chip, and has an electronic, not physical shutter. This has some real implications for photogrammetry which we won't address here.

* $50 camera
* 7.564 (H) x 5.476 (V) mm
* $25, 6mm lens

Using a [field of view calculator](https://zwww.scantips.com/lights/fieldofview.html), this gives us 49.06° vertical field of view, 64.38° horizontal. To create a 360° array, we would need 6 (H) or 7 (V) cameras mounted, which would total $450-$525, which is approximately the price of a single Sony α6000.
