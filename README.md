# kindle-news-feeds-display
 
This repo is display bbc & cnn news feeds on old kindle 3

### Screenshot
<img src="screenshot.jpg" width="300" alt="Kindle 3 screenshot" />

## Setup
### kindle
1. jailbreak your Kindle
2. access to kindle via usbnet:
```
ip a add 192.16.2.1/24 dev usb0
ip link set usb0 up
ssh root@192.168.2.2 (no password)
```
3. create a directory and mount tmpfs:
```
mntroot rw
mkdir /www
mount -t tmpfs tmpfs /www
mntroot ro
```
4. copy kindle/kindle-news-feeds and kindle/launchpad to /mnt/us folder:
```
scp kindle/kkindle-news-feeds kindle/launchpad root@192.168.2.2:/tmp
ssh root@192.168.2.2 (no password)
mv /tmp/kindle-news-feeds /mnt/us
mv /tmp/launchpad/* mnt/us/launchpad
```
5. create a file
```
touch /mnt/us/kindle-news-feeds/enable
```
6. edit /etc/fstab: 
```
tmpfs             /www          tmpfs  defaults,size=16m 0 0
```
7. setup cron: (example)
```
/etc/crontab/root
20,25,50,55 * * * * sh /mnt/us/kindle-news-feeds/script.sh
```
8. setup usbnet:
```
cd /mnt/us/usbnet
cp DISABLED_auto auto
mv DISABLED_auto DISABLED_auto.orig
```
9. disable kindle
```
/etc/init.d/powerd stop
/etc/init.d/framework stop
```
10. optionally install kindle-debian, system can improve

### server
1. get free subscription plan from openweathermap.org
2. setup usbnet:
```
usbnet: /etc/network/interfaces
    
    auto usb0
      iface usb0 inet static
      address 192.168.2.1
      netmask 255.255.255.0
      broadcast 192.168.2.255
      network 192.168.2.0
```
3. copy kindle-weather-host to server:
```
cp -a host-server/var/lib/kindle-weather-host /var/lib
```
4. install packages and setup: (eg. debian buster)
```
    image processors:
    apt install imagemagick imagemagick-6-common imagemagick-6.q16 \
      imagemagick-common libgraphicsmagick-q16-3 libmagickcore-6.q16-6 \
      libmagickcore-6.q16-6-extra libmagickwand-6.q16-6 pngcrush potrace

    graphicsmagick:
    apt install graphicsmagick libgraphicsmagick++-q16-12 libgraphicsmagick-q16-3

    EDIT: /usr/lib/GraphicsMagick-1.3.35/config/type.mgk
      
<?xml version="1.0"?>
<typemap>
  <include file="type-ghostscript.mgk" />
  <include file="type-kindle.mgk" /> 
</typemap>

    ADD: /usr/lib/GraphicsMagick-1.3.35/config/type-kindle.mgk
       
<?xml version="1.0"?>
<typemap>
  <type
    name="Droid-Sans"
    fullname="Droid Sans"
    family="Droid Sans"
    weight="400"
    style="normal"
    stretch="normal"
    glyphs="/root/.fonts/Delicious/Sans_Regular.ttf"
    />
  <type
    name="Sans-Bold"
    fullname="Sans-Bold"
    family="Droid Sans"
    weight="700"
    style="normal"
    stretch="normal"
    glyphs="/root/.fonts/Delicious/Sans_Bold.ttf"
    />
  <type
    name="Sans-Bold-Italic"
    fullname="Sans Bold Italic"
    family="Droid Sans"
    weight="700"
    style="italic"
    stretch="normal"
    glyphs="/root/.fonts/Delicious/Sans_BoldItalic.ttf"
    />
  <type
    name="Sans-Italic"
    fullname="Sans Italic"
    family="Droid Sans"
    weight="400"
    style="italic"
    stretch="normal"
    glyphs="/root/.fonts/Delicious/Sans_Italic.ttf"
    />
</typemap>

    web server:
    apt install nginx-light

    firewall:
    apt install shorewall
    
    EDIT: /etc/shorewall/interfaces
    choose the right interface
    
    ntp server:
    apt install ntp
```
5. install python3 modules: feedparser, requests, lxml
```
apt install python3-feedparser python3-lxml python3-pil python3-pip \
  python3-requests python3-wheel python3-fontconfig python3-setuptools \
  python3-astral
    
pip3 install pytz
```
6. setup font:
```
apt install fontconfig

extract a ttf archive and copy ttf fonts to /root/.fonts folder

fc-cache -v -f
```
7. setup cron: (example)
```
/etc/cron.d/kindle-news-feeds

15 * * * * root sh -c "/var/lib/kindle-news-feeds-host/kindle-news-feeds.sh"
21 */2 * * * root sh -c "/var/lib/kindle-news-feeds-host/kindle-news-feeds.sh settings-bbc-business.xml"
21 1-23/2 * * * root sh -c "/var/lib/kindle-news-feeds-host/kindle-news-feeds.sh settings-bbc-technology.xml"
45 * * * * root sh -c "/var/lib/kindle-news-feeds-host/kindle-news-feeds.sh settings-cnn-World.xml"
51 */2 * * * root sh -c "/var/lib/kindle-news-feeds-host/kindle-news-feeds.sh settings-cnn-football.xml"
51 1-23/2 * * * root sh -c "/var/lib/kindle-news-feeds-host/kindle-news-feeds.sh settings-cnn-Entertainment.xml"
```

### setting
Edit settings.xml

### dark mode
If enable dark mode, edit display.xml.
```
<dark_mode>
True: dark mode
False or None: light mode
Auto: automatic switch between light mode and dark mode according to the time of sunrise and sunset

<lat>
latitude

<lng>
longitude

<timezone>
tz database name
```
<img src="sample_images/cnn-world-dark-mode.png" width="300" alt="kindle news feeds - dark mode" />

### italic
To enable italic text in summary, edit settings.xml.
````
<italic>True</italic>
````
