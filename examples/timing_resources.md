# Documents and resources for timing

## Building a Network Time Protocol (NTP) server

- [The Wikipedia page for NTP](https://en.m.wikipedia.org/wiki/Network_Time_Protocol) has a lot of good background info.
- Here is [a ridiculously detailed recipe for a stratum 1 NTP server on a Pi](https://www.satsignal.eu/ntp/Raspberry-Pi-NTP.html).
- And a [slightly more lightweight recipe](https://www.satsignal.eu/ntp/Raspberry-Pi-quickstart.html) from the same guy
- Would you have expected Florida Man to be helpful here? Me neither. Nevertheless, the South Florida Amateur Astronomers Association has provided a nice write-up of a [Pi-based, GPS PPS-driven NTP server](https://www.slsmk.com/how-to-setup-a-gps-pps-ntp-time-server-on-raspberry-pi/)
- We could also use an Arduino. Here's [a forum post with some leads on that, plus a downloadable sketch](https://forum.arduino.cc/index.php?topic=197870.0)

## Testing and syncing
- Here is a [recipe for building a test rig with a millisecond-precise time display](https://www.instructables.com/id/High-speed-Clock-for-Slow-motion-Videos/)

## More bits of GPS info
- [A detailed explanation of NMEA](http://www.gpsinformation.org/dale/nmea.htm)
- [The Wikipedia page on NMEA](https://en.wikipedia.org/wiki/NMEA_0183) is pretty good too.
- More background on [GPSD](https://ozzmaker.com/using-python-with-a-gps-receiver-on-a-raspberry-pi/), which is the easiest way to sync time from the PPS pulse.
- A Python library for [parsing NMEA](https://github.com/Knio/pynmea2); very useful and transparent. I have a high bar for using a library instead of writing my own code to parse this kind of data, but this is definitely worth using.

## Hardware and wiring
- [Good diagrams of Pi Zero pinouts](https://pi4j.com/1.2/pins/model-zero-rev1.html)
