# phpVirtualBox

# About

phpVirtualBox it is a web interface to manage and access VirtualBox machines.

VirtualBox is a powerful hypervisor for x86-64 (and from v5.0 also supporting IA-32/x86-32) architechtures, developed by Oracle Corporation.
VirtualBox was originally created by InnoTek Systemberatung GmbH, which was acquired by Sun Microsystems in 2009, 
which was in turn acquired by Oracle in 2010 (VirtualBox initial release: 17 January 2007)

This repository is a fork of phpVirtualBox, which seems no longer supported by the official authors
(last commit was sent on Jan 27, 2021) checked on March 2024

Basically this software is a fork from BartekSz95's phpVirtualBox and his various contributors with some additions from REMORA team.
 ( see https://github.com/BartekSz95/phpvirtualbox/graphs/contributors )

phpVirtualBox is from 2017 maintained by Smart Guide Pty Ltd (tudor at smartguide dot com dot au) with support from various contributors
 ( see https://github.com/phpvirtualbox/phpvirtualbox/graphs/contributors )

In time a lot of forks of the software appeared (see https://github.com/phpvirtualbox/phpvirtualbox/forks )

Originally Copyright (C) 2015 Ian Moore (imoore76 at yahoo dot com) 


FREE, WITHOUT WARRANTY:

All files of this program (phpVirtualBox) are distributed under the terms contained in
the LICENSE.txt file in this folder unless otherwise specified in an individual source file.
By using this software, you are agreeing to the terms contained therein.
If you have not received and read the license file, or do not agree with its conditions,
please cease using this software immediately and remove any copies you may have in your possession.

# Installation

## zip file

1) Download zip file from GitHub project site: https://github.com/yremora/phpvirtualbox/archive/master.zip

2) Unzip the zipfile into a folder accessible by your web server

3) Rename config.php-example to config.php and edit as needed.


## rpm package
### Mageia OS
[done] phpvirtualbox-7.0.14-99.mga9 (works with virtualbox-7.0.14-99.mga9 + dkms-virtualbox-7.0.14-99.mga9 + virtualbox-kernel-6.6.14-desktop-2.mga9-7.0.14-99.mga9 + virtualbox-kernel-6.6.14-server-2.mga9-7.0.14-99.mga9)

## deb package 
TODO

# Post installation

Default login is username: admin password: admin

# Password Recovery

Rename the file recovery.php-disabled to recovery.php, navigate to it in
your web browser, and follow the instructions presented.


# Additional
Read the wiki section for more information
 ( see https://github.com/yremora/phpvirtualbox/wiki )

Please report bugs / feature requests to yremora@GitHub
 ( see https://github.com/yremora/phpvirtualbox/issues )
