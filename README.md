# vlc-multiview
VLC multiviewer in python

-- About --

Just a "get it working" extention of a GPL's gtk/python/vlc example allowing multiple video (or audio) streams on a screen. 
I mainly use it for local multicast RTP sources, but anything vlc will play should work

![Sample view](mv.png)

-- Config format --

udp://@:1234 #Channel name

Where "udp://@:1234" is the URL to load
And Channel name is the name to display

Left click on a viewer and it unmutes the viewer
Middle click on a viewer to drop volume
Right click on a viewer to increase volume


-- History --

Originally envisaged to run on a pi with a touchscreen to monitor some broadcast feeds, but on testing it felt like VLC struggled to decode 16x30mbit multicast streams. Requirement went away so made no more progress. 

Reused the code to take in 9x c. 5-10mbit unicast streams fitlet for covid-enabled remote monitoring, driven by a mouse, hence adding the volume control. 


