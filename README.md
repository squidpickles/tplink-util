tplink-util
===========
This is a Python implementation of the TL-WPA4220KIT utility, originally
available only for Windows. It allows users to find the devices' HTTP
configuration pages.

Requirements
============
 * Python 3
 * netifaces (https://pypi.python.org/pypi/netifaces)
 * One or more TL-WPA4220KIT devices

Usage
=====
    $ python tplink-util.py
    IP address        MAC address         Model No.      Description
    ================================================================
    10.20.26.222      e8:de:a7:4d:5a:cc   TL-WPA4220   11N Powerline AP
    10.20.26.44       e8:94:06:2e:ab:23   TL-WPA4220   11N Powerline AP

You can get to the configuration utility by visiting one of the IP addresses in your web browser:

    http://10.20.26.222

The default username/password is admin/admin

License
=======
Copyright 2013 Kevin Rauwolf

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
