# This file is part of the YREMORA https://YREMORA.com
#
# Copyright (C) 2024 YREMORA
#
# This software is distributed under multiple licenses;
# see the COPYING file in the main directory for licensing
# information for this specific distribution.
#
# This use of this software may be subject to additional restrictions.
# See the LEGAL file in the main directory for details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

# decide if systemd is present or not
%define systemd %(test -x /usr/bin/systemctl && echo 1 || echo 0)

# rewrite the ostype macro because of the subreleases of the kernel in CentOS that could break old macro
%define ostype %(awk '{for(i=1;i<=NF;i++)if($i=="release")print $1,substr($(i+1),1,1)}' /etc/redhat-release)

# Amazon Linux and Oracle Linux do not have /etc/redhat-release file, but they have /etc/system-release
%{!?ostype:%define ostype %(awk '{for(i=1;i<=NF;i++)if($i=="release")print $1,substr($(i+1),1,1)}' /etc/system-release)}

# define dist if not exist
%{!?dist:%define dist %{?distsuffix:%distsuffix%{?product_version}}}

# define Suggests and Recommends in spec (if rpm does not supports them: automatically comment them out with ##)
%define Suggests() %(LANG=C LC_MESSAGES=C rpm --help | fgrep -q ' --suggests ' && echo "Suggests:" || echo "##")
%define Recommends() %(LANG=C LC_MESSAGES=C rpm --help | fgrep -q ' --recommends ' && echo "Recommends:" || echo "##")

# define build number and tarball name
%define buildnum 99
%{!?tarname:%define tarname %{name}-%{version}}

# define datadir and wwwdir variables
%define datadir %{_datadir}/%{name}
%define wwwdir  %{_var}/www/%{name}

Name:		phpvirtualbox
Version:	7.0.14
Release:	%{buildnum}%{?gitver:.git%{gitver}}%{?dist}
Group:		Networking/WWW
License:	GPLv3
Packager:	REMORA <support@YREMORA.com>
Vendor:		REMORA (phpVirtualBox https://github.com/phpvirtualbox/)
URL:		https://yremora.com
Source:		%{tarname}.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{release}
BuildArch:	noarch
# TODO add requires based on Linux version (dist)
#Requires	: php >= 5.2, php-soap, httpd apache2 php5 php5-mysql libapache2-mod-php5 php-soap
Requires:	webserver-base
Requires:	php-webinterface
Requires:	config(apache-mod_php)
Requires:	php > 5.4
Requires:	php-soap
Requires:	virtualbox >= %{version}
Requires(post):	rpm-helper
Conflicts:	virtualbox-kernel-desktop-latest
Summary:	A web-based front-end to VirtualBox written in PHP


%description
An open source, AJAX implementation of the VirtualBox user interface written in PHP.
As a modern web interface, it allows you to access and control remote VirtualBox instances.
phpVirtualBox was designed to allow users to administer VirtualBox in a headless environment.
By mirroring the VirtualBox GUI through this web interface you will get full control over all VMs.
Performs all VirtualBox administration actions through vboxwebsrv (a SOAP server distributed with VirtualBox) 
It does not directly interact with any files on the VirtualBox host.
Might be used in a "hosting" environment where the concept of VM ownership is required.
phpVirtualBox version MUST align with VirtualBox version
Configure automatic VM start / stop functionality on system boot from:
VM - Settings --> General --> Basic --> StartupMode --> Automatic


%prep
%global debug_package %{nil}
%setup -q -n %{name}

# add Mageia OS icons in js/utils.js
#sed -i 's/"os_mandriva_64.png"; break;/"os_mandriva_64.png"; break;\n\t\tcase "Mageia":\t\tstrIcon = "os_mageia.png"; break;\n\t\tcase "Mageia_64":\tstrIcon = "os_mageia_64.png"; break;/' js/utils.js
# add Alma Linux and Amazon Linux OS icons
#sed -i 's/"os_linux26_64.png"; break;/"os_linux26_64.png"; break;\n\t\tcase "AlmaLinux":\tstrIcon = "os_alma.png"; break;\n\t\tcase "AlmaLinux_64":\tstrIcon = "os_alma_64.png"; break;/' js/utils.js
#sed -i 's/"os_alma_64.png"; break;/"os_alma_64.png"; break;\n\t\tcase "AmazonLinux":\tstrIcon = "os_amazon.png"; break;\n\t\tcase "AmazonLinux_64":\tstrIcon = "os_amazon_64.png"; break;/' js/utils.js



%build
# no build needed, just copy files

%install
# rename files
%{__mv} CHANGELOG.txt CHANGELOG
%{__mv} LICENSE.txt LICENSE
%{__mv} README.md README

# put files in place
%{__mkdir_p} %{buildroot}%{datadir}
FILES="index.html config.php-example phpvirtualbox.conf docker-compose.yml Dockerfile recovery.php-disabled vboxinit GPLv3.txt CHANGELOG LICENSE README"
DIRECS="css endpoints images js languages panes rdpweb tightvnc"
for i in ${FILES} ${DIRECS}; do
    %{__cp} -a ./${i} %{buildroot}%{datadir}/${i}
    %{__cp} -a packaging %{buildroot}%{datadir}/
done

# create a default instance/location of which other instances can be copied
%{__mkdir_p} %{buildroot}%{wwwdir}
pushd %{buildroot}%{wwwdir}/
%{__cp} %{buildroot}/%{datadir}/config.php-example %{buildroot}%{datadir}/config.php
%{__cp} -a %{buildroot}%{datadir}/* %{buildroot}%{wwwdir}/

if [[ ! -f %{buildroot}/etc/httpd/conf/sites.d/phpvirtualbox.conf ]] ; then
    mkdir -p %{buildroot}%{webappconfdir}
    cp %{buildroot}%{datadir}/phpvirtualbox.conf %{buildroot}%{webappconfdir}
fi

popd


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{datadir}
%attr(-,apache,apache) %{wwwdir}
%{webappconfdir}/%{name}.conf


%pre
# pre section: before installation

%preun
# preun section: before uninstallation

%post
# post section: after installation
installdate=$(date)

# if first installation ($1=1) or update ($1=2)
#if [ $1 = 1 ] || [ $1 = 2 ]; then
user=vbox
check_user="`/usr/bin/id ${user} 2>/dev/null`"
if [[ "${check_user}" = "" ]];then
    # add the vbox user in vboxusers group
    /usr/share/rpm-helper/add-user phpvirtualbox $1 vbox /home/vbox /bin/bash
    # generate random password
    pass=`(hostname; dd if=/dev/urandom bs=64 count=1; date '+%s') 2>/dev/null | md5sum | sed 's/ .*$//'`
    echo "$pass" | passwd --stdin vbox 2>/dev/null
    # replace password in config.php 
    sed -i "s/'pass';$/'$pass';/" /var/www/phpvirtualbox/config.php
    # creating the VMs and iso directories
    [[ -d /home/vbox/VMs ]] || mkdir -p /home/vbox/VMs
    [[ -d /home/vbox/iso ]] || mkdir -p /home/vbox/iso
    [[ -d /home/vbox/.VirtualBox ]] || mkdir -p /home/vbox/.VirtualBox
fi

if [[ -f /etc/default/virtualbox ]] ; then
    if [ -z "`grep "updated by" /etc/default/virtualbox`" ]; then
	sed -i "1 i # updated by ${name}-${version} on ${installdate}/" /etc/default/virtualbox
    fi
fi

# /etc/httpd/conf/vhosts.d/phpvirtualbox.php file defilement
sed -i 's@^Alias /phpvirtualbox /usr/share/phpvirtualbox@Alias /vbox /var/www/phpvirtualbox\n# Alias /phpvirtualbox /var/www/phpvirtualbox@' /etc/httpd/conf/sites.d/phpvirtualbox.conf
sed -i 's@^Require local@# Require local@' /etc/httpd/conf/sites.d/phpvirtualbox.conf

# hide notice for mismatch versions (phpVirtualBox vs VirtualBox)
#sed -i "s/\] != vStr) {/\] \!\= vStr \&\& vers\[0\]+'.'+vers\[1\] \!\= '5.1' ) {/" %{buildroot}%{wwwdir}/js/chooser.js

# config.php file defilement
# set preview interval to 30 seconds
sed -i 's/#var $previewUpdateInterval = 30;/var $previewUpdateInterval = 90;/' %{wwwdir}/config.php
# restrict access only to /home/vbox/iso and /home/vbox/VMs
sed -i 's^#var $browserRestrictFolders .*^var $browserRestrictFolders = array(\x27/home/vbox/iso\x27,\x27/home/vbox/VMs\x27);^' %{wwwdir}/config.php
# extend the interval for memory check
sed -i 's/var $hostMemInfoRefreshInterval = 5;/var $hostMemInfoRefreshInterval = 60;/' %{wwwdir}/config.php
# remove the 640x480 resolution from the array
sed -i 's/var $consoleResolutions = .*/var $consoleResolutions = array(\x27800x600\x27,\x271024x768\x27,\x271280x720\x27,\x271440x900\x27);/' %{wwwdir}/config.php
# enable VM startup option from config.php - uses vboxinit
sed -i 's/^#var $startStopConfig = true/var $startStopConfig = true/' %{wwwdir}/config.php
# increase RDP port range
sed -i 's/9000-9100/3390-9100/' %{wwwdir}/config.php
# enable/enforce VM ownership ( will preceed each VM and hard disk with username_ )
sed -i 's/#var $enforceVMOwnership/var $enforceVMOwnership/' %{wwwdir}/config.php

chown -R vbox:vbox /home/vbox
usermod -a -G vboxusers vbox
usermod -a -G daemon vbox

# change default storage directory from 'VirtualBox VMs' to VMs via VBoxManage utility
/usr/bin/su - vbox -c 'VBoxManage setproperty machinefolder "/home/vbox/VMs/"'
VBoxManage setproperty machinefolder "/home/vbox/VMs/"

# change External authentication library from 'VBoxAuth' to 'null'
/usr/bin/su - vbox -c "VBoxManage setproperty websrvauthlibrary null"
VBoxManage setproperty websrvauthlibrary null

# add VirtualBox Extension Pack needed for VRDP (remote display)
root_check_ext="`/usr/bin/VBoxManage list extpacks|grep -A 1 'Oracle VM VirtualBox Extension Pack'|wc -l`"
if [[ "${root_check_ext}" != 2 ]];then
echo "Installing Oracle VM VirtualBox Extension Pack"
#echo Y|/usr/bin/su - vbox -c "VBoxManage extpack install --replace /usr/share/phpvirtualbox/packaging/Oracle_VM_VirtualBox_Extension_Pack-7.0.14.vbox-extpack --accept-license=33d7284dc4a0ece381196fda3cfe2ed0e1e8e7ed7f27b9a9ebc4ee22e24bd23c"
echo Y|VBoxManage extpack install --replace /usr/share/phpvirtualbox/packaging/Oracle_VM_VirtualBox_Extension_Pack-7.0.14.vbox-extpack --accept-license=33d7284dc4a0ece381196fda3cfe2ed0e1e8e7ed7f27b9a9ebc4ee22e24bd23c
else
#echo "Oracle VM VirtualBox Extension Pack `VBoxManage list extpacks|grep -A 1 'Oracle VM VirtualBox Extension Pack'|tail -n 1|sed 's/        / /'`is already installed"
ext_version="`/usr/bin/VBoxManage list extpacks|grep -A 1 'Oracle VM VirtualBox Extension Pack'|tail -n 1|sed 's/        / /'`"
echo "Oracle VM VirtualBox Extension Pack ${ext_version} is already installed"
fi

# check already existing VMs, send a message to journalctl via systemd-cat
# count VMs
count_vms=0
for dir in `ls /home/vbox/VMs`;do
    if [ -d "/home/vbox/VMs/$dir" ]; then
	if [ -f "/home/vbox/VMs/$dir/$dir.vbox" ];then
	    count_vms=$((count_vms+1))
	    echo -e "Found file /home/vbox/VMs/$dir/$dir.vbox, if VM is not present or visible in PHPVirtualBox web interface" |/usr/bin/systemd-cat
	    echo -e "use command: su - vbox -c \"VBoxManage registervm /home/vbox/VMs/$dir/$dir.vbox\"\n" |/usr/bin/systemd-cat
	fi
    fi
done
echo -e "Found $count_vms in /home/vbox/VMs, see more details with: journalctl -g VMs"

# VBoxHost (VirtualBox kernel modules) VBoxWeb (VirtualBox Web Service) and HTTPD/Apache enable/restart
/usr/bin/systemctl daemon-reload >/dev/null 2>&1
/usr/bin/systemctl enable vboxhost.service >/dev/null 2>&1
/usr/bin/systemctl restart vboxhost.service >/dev/null 2>&1
/usr/bin/systemctl enable vboxweb.service >/dev/null 2>&1
/usr/bin/systemctl restart vboxweb.service >/dev/null 2>&1
/usr/bin/systemctl enable httpd.service >/dev/null 2>&1
/usr/bin/systemctl restart httpd.service >/dev/null 2>&1


%postun
# after uninstallation
/usr/bin/systemctl daemon-reload >/dev/null 2>&1
#if [ $1 = 0 ] ; then
#echo Uninstalling %{name}
#fi


%changelog
* Thu Feb 29 2024 YREMORA <support@YREMORA.com> 7.0-14
- Initial rebuild for Mageia Linux OS using web files from PHPVirtualBox v7.0-rc1
- adaptation of BartekSz @ github https://github.com/BartekSz95
- config.php defilement (see post section of .spec file)
- See previous changelog entries to understand the path of this package

* Tue Jan 10 2023 - BartekSz95@github v7.0-rc1
- https://www.Bartek-Sz.pl/ Korzeniewo, Poland
- Support for VirtualBox 7.0 (release candidate 1) and PHP8.2
- Fixed clone option and encryption/decryption
- Fixes for few small bugs

* Fri Nov 9 2018 <h6w@github.com> - 6.0-0   
- Upgrade to Virtualbox 6.0

* Fri Nov 09 2018 - 5.2-1
- Various snapshot fixes and improvements - @Adam5Wu
- Add a configuration variable to set the VRDE address - @rosorio
- New icons to match Desktop Application - @der-eismann
- Fix Import/Export - @tom077
- Russian translation fixes - @SvetlanaTkachenko
- Viewport and URL fixes - @krzysztof113
- Convert to unix file format to reduce size

* Fri Feb 16 2018 - 5.2-0
- Long overdue post 5.0 support (5.2 at this stage)
- PHP 7.1 support thanks to @mikedld
- New Czech localization thanks to @p-bo
- MySQL autho module thanks to @tioigor96
- Various bugfixes thanks to @tschoening and @ashway83
- Huge support effort from @tom077!
- Thanks to everyone who's helped bring this project back up to speed!

* Fri Jan 8 2016 - 5.0-5
- PHP 7 support was added

* Mon Dec 7 2015 - 5.0-4
- Fixed bug in file / folder browser when $browserRestrictFolders is set.
https://sourceforge.net/p/phpvirtualbox/bugs/50/
- Fixed bug in host network interface sorting.
https://sourceforge.net/p/phpvirtualbox/bugs/36/
- Fixed bug where phpVirtualBox installations on the same server may
share session cookies in certain PHP configurations.
- Fixed bug where noPreview=true; was ignored in settings.
https://sourceforge.net/p/phpvirtualbox/bugs/38/

* Wed Sep 9 2015 - 5.0-3
- Fixed file browser header content type causing blank file
https://sourceforge.net/p/phpvirtualbox/bugs/49/
- Fixed selection highlighting in file / folder browser
- Fixed all VMs in a group starting on the same RDP port 
https://sourceforge.net/p/phpvirtualbox/bugs/46/
- Fixed missing en.xml language file 
https://sourceforge.net/p/phpvirtualbox/bugs/45/

* Wed Aug 12 2015 - 5.0-2
- Translation fixes
- Fixed error when creating host-only networks
- Fixed host-only network DHCP server settings
- Fix USB device attaching / detaching from Settings menu of a running VM.

* Thu Aug 06 2015 stephane de labrusse <stephdl@de-labrusse.fr> 5.0.0-1
- require to phpvirtualbox-5.0

* Sun May 18 2014 stephane de labrusse <stephdl@de-labrusse.fr> 4.3.1-3
- first release to sme9
- unixgroup removed from the contribs
- fix ssl redirection

* Wed Mar 19 2014 stephane de labrusse <stephdl@de-labrusse.fr> 4.3.1-1
- due to the bug correction of phpvirtualbox, this version give back the web authentication with migrate fragment update

* Wed Jan 08 2014 JP Pialasse <tests@pialasse.com> 4.3.0-10.sme
- changing requires to phpvirtualbox = 4.3

* Mon Dec 30 2013 JP Pialasse <tests@pialasse.com> 4.3.0-9.sme
- renaming to import into buildsys

* Fri Dec 13 2013 stephane de labrusse <stephdl@de-labrusse.fr> 4.3.0-8
- remove the web authentication for the buildin phpvirtualbox authentication

* Sun Nov 10 2013 stephane de labrusse <stephdl@de-labrusse.fr> 4.3.0-7
- removing dependance to smeserver-virtualbox-4.3

* Tue Nov 05 2013 stephane de labrusse <stephdl@de-labrusse.fr> 4.3.0-6
- change name to match the phpvirtualbox version

* Wed Oct 23 2013 stephane de labrusse <stephdl@de-labrusse.fr> 4.3.0-5
- Clean 92phpvirtualbox to force only the localnetwork
- Add the plugin unixgroup (from pwauth) to allow unix groups to reach the apache server.
- you can see http://code.google.com/p/pwauth/ for more informations

* Sun Oct 20 2013 stephane de labrusse <stephdl@de-labrusse.fr> 4.3.0-4
- Force https protocol for phpvirtualbox

* Sat Oct 19 2013 stephane de labrusse <stephdl@de-labrusse.fr> 4.3.0-3
- Initial build, forked from http://phpvirtualbox.googlecode.com and jsosic .spec
- note added by YREMORA

* Thu Aug 15 2013 Jakov Sosic <jsosic@srce.hr> - 4.2-7
- bump to 4.2-7

* Tue Feb 12 2013 Jakov Sosic <jsosic@srce.hr> - 4.2-4.2
- added lib/config.php patch to enable import of local configuration

* Mon Feb 11 2013 Jakov Sosic <jsosic@srce.hr> - 4.2-4.1
- Initial build.
