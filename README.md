# kindle-news-feeds-display
 
This repo is display bbc news feeds on old kindle 3

### Screenshot
<img src="screenshot.jpg" width="300" alt="Kindle 3 screenshot" />

## Setup
### kindle
1. jailbreak your Kindle
2. copy kindle/kindle-weather to /mnt/us folder
3. setup cron
5. setup usbnet: rename to /mnt/us/usbnet/auto
4. optionally install kindle-debian, system can improve

### server
1. get free subscription plan from openweathermap.org
2. setup usbnet
3. copy host-server/var/lib/kindle-weather-host to /var/lib folder
4. install packages and setup (eg. debian buster)
5. install python3 modules: feedparser, requests, lxml
6. setup font
7. setup cron

```
    usbnet: /etc/network/interfaces
    
    auto usb0
      iface usb0 inet static
      address 192.168.2.1
      netmask 255.255.255.0
      broadcast 192.168.2.255
      network 192.168.2.0

    python modules:
    apt install python3-feedparser python3-lxml python3-pil python3-pip \
    python3-requests python3-wheel python3-fontconfig python3-setuptools

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
    
    ntp server:
    apt install ntp

    font:
    apt install fontconfig

    extract a ttf archive and copy ttf fonts to /root/.fonts folder
    fc-cache -v -f
```

## setting
Edit settings.xml
