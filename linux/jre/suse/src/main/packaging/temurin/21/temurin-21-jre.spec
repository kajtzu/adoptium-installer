%global upstream_version 21+35
# Only [A-Za-z0-9.] allowed in version:
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Versioning/#_upstream_uses_invalid_characters_in_the_version
# also not very intuitive:
#  $ rpmdev-vercmp 21.0.0.0.0___21.0.0.0.0+1
#  20.0.0.0.0___1 == 21.0.0.0.0+35
%global spec_version 21.0.0.0.0.35
%global spec_release 1
%global priority 2100

%global source_url_base https://github.com/adoptium/temurin21-binaries/releases/download
%global upstream_version_url %(echo %{upstream_version} | sed 's/\+/%%2B/g')
%global upstream_version_no_plus %(echo %{upstream_version} | sed 's/\+/_/g')
%global java_provides openjre

# Map architecture to the expected value in the download URL; Allow for a
# pre-defined value of vers_arch and use that if it's defined

%ifarch x86_64
%global vers_arch x64
%global vers_arch3 aarch64
%global src_num 0
%global sha_src_num 1
%endif
%ifarch aarch64
%global vers_arch x64
%global vers_arch3 aarch64
%global src_num 4
%global sha_src_num 5
%endif
# Allow for noarch SRPM build
%ifarch noarch
%global src_num 0
%global sha_src_num 1
%endif

Name:        temurin-21-jre
Version:     %{spec_version}
Release:     %{spec_release}
Summary:     Eclipse Temurin 21 JRE

Group:       java
License:     GPLv2 with exceptions
Vendor:      Eclipse Adoptium
URL:         https://projects.eclipse.org/projects/adoptium
Packager:    Eclipse Adoptium Package Maintainers <temurin-dev@eclipse.org>

AutoReqProv: no
Prefix: %{_libdir}/jvm/%{name}

ExclusiveArch: x86_64 aarch64

BuildRequires:  tar
BuildRequires:  wget

Requires: /bin/sh
Requires: /usr/sbin/alternatives
Requires: ca-certificates
Requires: dejavu-fonts
Requires: libX11-6%{?_isa}
Requires: libXext6%{?_isa}
Requires: libXi6%{?_isa}
Requires: libXrender1%{?_isa}
Requires: libXtst6%{?_isa}
Requires: libasound2%{?_isa}
Requires: glibc%{?_isa}
Requires: libz1%{?_isa}
Requires: fontconfig%{?_isa}

Provides: jre
Provides: jre-21
Provides: jre-21-headless
Provides: jre-21-%{java_provides}
Provides: jre-21-%{java_provides}-headless
Provides: jre-headless
Provides: jre-%{java_provides}
Provides: jre-%{java_provides}-headless

# First architecture (x86_64)
Source0: %{source_url_base}/jdk-%{upstream_version_url}/OpenJDK21U-jre_%{vers_arch}_linux_hotspot_%{upstream_version_no_plus}.tar.gz
Source1: %{source_url_base}/jdk-%{upstream_version_url}/OpenJDK21U-jre_%{vers_arch}_linux_hotspot_%{upstream_version_no_plus}.tar.gz.sha256.txt
# Third architecture (aarch64)
Source4: %{source_url_base}/jdk-%{upstream_version_url}/OpenJDK21U-jre_%{vers_arch3}_linux_hotspot_%{upstream_version_no_plus}.tar.gz
Source5: %{source_url_base}/jdk-%{upstream_version_url}/OpenJDK21U-jre_%{vers_arch3}_linux_hotspot_%{upstream_version_no_plus}.tar.gz.sha256.txt

# Avoid build failures on some distros due to missing build-id in binaries.
%global debug_package %{nil}
%global __brp_strip %{nil}

%description
Eclipse Temurin JRE is an OpenJDK-based runtime environment to execute
applications and components using the programming language Java.

%prep
pushd "%{_sourcedir}"
sha256sum -c "%{expand:%{SOURCE%{sha_src_num}}}"
popd

%setup -n jdk-%{upstream_version}-jre -T -b %{src_num}

%build
# noop

%install
mkdir -p %{buildroot}%{prefix}
cd %{buildroot}%{prefix}
tar --strip-components=1 -C "%{buildroot}%{prefix}" -xf %{expand:%{SOURCE%{src_num}}}

# Use cacerts included in OS
rm -f "%{buildroot}%{prefix}/lib/security/cacerts"
pushd "%{buildroot}%{prefix}/lib/security"
ln -s /var/lib/ca-certificates/java-cacerts "%{buildroot}%{prefix}/lib/security/cacerts"
popd

%pretrans
# noop

%post
if [ $1 -ge 1 ] ; then
    update-alternatives --install %{_bindir}/java java %{prefix}/bin/java %{priority} \
                        --slave %{_bindir}/jfr jfr %{prefix}/bin/jfr \
                        --slave %{_bindir}/jrunscript jrunscript %{prefix}/bin/jrunscript \
                        --slave %{_bindir}/jwebserver jwebserver %{prefix}/bin/jwebserver \
                        --slave %{_bindir}/keytool keytool %{prefix}/bin/keytool \
                        --slave %{_bindir}/rmiregistry rmiregistry %{prefix}/bin/rmiregistry
fi

%preun
if [ $1 -eq 0 ]; then
    update-alternatives --remove java %{prefix}/bin/java
fi

%files
%defattr(-,root,root)
%{prefix}

%changelog
%changelog
* Wed Sep 20 2023 Eclipse Adoptium Package Maintainers <temurin-dev@eclipse.org> 21.0.0.0.0.35-1
- Eclipse Temurin 21.0.0+35 release 0.
