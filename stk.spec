%define	major		4
%define	libname		%mklibname %{name} %{major}
%define	develname	%mklibname -d %{name}

Name:		stk
Version:	4.4.4
Release:	1
Summary:	Synthesis ToolKit in C++
Group:		Sound
License:	MIT
URL:		http://ccrma.stanford.edu/software/stk/
# Original tarfile can be found at %%{url}/release/%%{name}-%%{version}.tar.gz
# We remove legally questionable files as well as accidentally packed
# object files.
Source0:	%{name}-%{version}.stripped.tar.gz
Source1:	README.fedora
Source100:	%{name}.rpmlintrc
Patch0:		%{name}-%{version}-header.patch
Patch1:		%{name}-%{version}-cflags-lib.patch
Patch2:		%{name}-%{version}-sharedlib.patch
Patch3:		%{name}-%{version}-projects.patch
Patch4:		%{name}-%{version}-pthread.patch
BuildRequires:	pkgconfig(alsa)
BuildRequires:	pkgconfig(jack)
BuildRequires:	symlinks
BuildRequires:	autoconf

%description
The Synthesis ToolKit in C++ (STK) is a set of open source audio signal
processing and algorithmic synthesis classes written in the C++ programming
language. STK was designed to facilitate rapid development of music synthesis
and audio processing software, with an emphasis on cross-platform
functionality, realtime control, ease of use, and educational example code.
The Synthesis ToolKit is extremely portable (it's mostly platform-independent
C and C++ code), and it's completely user-extensible (all source included, no
unusual libraries, and no hidden drivers). We like to think that this
increases the chances that our programs will still work in another 5-10 years.
In fact, the ToolKit has been working continuously for about 10 years now. STK
currently runs with real-time support (audio and MIDI) on Linux, Macintosh OS
X and Windows computer platforms. Generic, non-realtime support has been
tested under NeXTStep, Sun, and other platforms and should work with any
standard C++ compiler.

#------------------------------------------------------------------------------

%package -n %{libname}
Summary:	Library for %{name}
Group:		System/Libraries

%description -n %{libname}
This package contains the main library for %{name}.

%files  -n %{libname}
%doc README
%{_libdir}/libstk.so.*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/rawwaves

#------------------------------------------------------------------------------

%package -n %{develname}
Summary:	Development files for %{name}
Group:		Development/C++
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}

%description -n %{develname}
The %{name}-devel package contains libraries and header files for developing
applications that use %{name}.

%files -n %{develname}
%doc README doc/* README.fedora
%{_libdir}/libstk.so
%{_includedir}/*

#------------------------------------------------------------------------------

%package demos
Summary:	Demo applications for %{name}
Group:		Sound
Requires:	tk >= 8.0
Requires:	%{libname} = %{version}

%description demos
The %{name}-demo package contains the demo applications for the C++ Sound
Synthesis ToolKit.

%files demos
%doc README README.fedora
%{_bindir}/%{name}-*
%{_bindir}/Md2Skini
%{_datadir}/%{name}/demo
%{_datadir}/%{name}/examples
%{_datadir}/%{name}/effects
%{_datadir}/%{name}/ragamatic
%{_datadir}/%{name}/eguitar

#--------------------------------------------------------------------------------

%prep
%setup0 -q
%patch0 -p1 -b .header
%patch1 -p1 -b .cflags
%patch2 -p1 -b .sharedlib
%patch3 -p1 -b .projects
%patch4 -p1 -b .pthread

# we patched configure.ac
autoconf -v

cp -a %{SOURCE1} README.fedora

# generated file
rm projects/examples/libMakefile

# remove backup files
find . -name '*~' -exec rm {} \;

# correct wrong perms
chmod 0644 src/LentPitShift.cpp
chmod 0644 include/LentPitShift.h

%build
# TODO: Fix build with oss support
%configure2_5x --with-jack --with-alsa RAWWAVE_PATH=%{_datadir}/stk/rawwaves/
%make -C src
%make -C projects/demo libdemo libMd2Skini
%make -C projects/examples -f libMakefile
%make -C projects/effects libeffects
%make -C projects/ragamatic libragamat
%make -C projects/eguitar libeguitar
#make %%{?_smp_mflags} -C projects/eguitar libeguitar


%install
mkdir -p \
    %{buildroot}%{_includedir}/stk \
    %{buildroot}%{_libdir} \
    %{buildroot}%{_bindir} \
    %{buildroot}%{_datadir}/stk/rawwaves \
    %{buildroot}%{_datadir}/stk/demo \
    %{buildroot}%{_datadir}/stk/examples \
    %{buildroot}%{_datadir}/stk/effects \
    %{buildroot}%{_datadir}/stk/ragamatic \
    %{buildroot}%{_datadir}/stk/eguitar

cp -p include/* %{buildroot}%{_includedir}/stk
cp -pd src/libstk.* %{buildroot}%{_libdir}
cp -p rawwaves/*.raw %{buildroot}%{_datadir}/stk/rawwaves

cp -pr projects/demo/tcl %{buildroot}%{_datadir}/stk/demo
cp -pr projects/demo/scores %{buildroot}%{_datadir}/stk/demo
cp -p projects/demo/demo %{buildroot}%{_bindir}/stk-demo
cp -p projects/demo/Md2Skini %{buildroot}%{_bindir}/Md2Skini
for f in Banded Drums Modal Physical Shakers StkDemo Voice ; do
    chmod +x projects/demo/$f
    sed -e 's,\./demo,%{_bindir}/stk-demo,' -e '1i#! /bin/sh' -i projects/demo/$f
    cp -p projects/demo/$f %{buildroot}%{_datadir}/stk/demo
done

cp -pr projects/examples/midifiles %{buildroot}%{_datadir}/stk/examples
cp -pr projects/examples/rawwaves %{buildroot}%{_datadir}/stk/examples
cp -pr projects/examples/scores %{buildroot}%{_datadir}/stk/examples
for f in sine sineosc foursine audioprobe midiprobe duplex play \
  record inetIn inetOut rtsine crtsine bethree controlbee threebees playsmf grains ; do
    cp -p projects/examples/$f %{buildroot}%{_bindir}/stk-$f
# absolute links, will be shortened later
    ln -s %{buildroot}%{_bindir}/stk-$f %{buildroot}%{_datadir}/stk/examples/$f
done

cp -pr projects/effects/tcl %{buildroot}%{_datadir}/stk/effects
cp -p projects/effects/effects %{buildroot}%{_bindir}/stk-effects
sed -e 's,\./effects,%{_bindir}/stk-effects,' -e '1i#! /bin/sh' \
  -i projects/effects/StkEffects
cp -p projects/effects/StkEffects %{buildroot}%{_datadir}/stk/effects

cp -pr projects/ragamatic/tcl %{buildroot}%{_datadir}/stk/ragamatic
cp -pr projects/ragamatic/rawwaves %{buildroot}%{_datadir}/stk/ragamatic
cp -p projects/ragamatic/ragamat %{buildroot}%{_bindir}/stk-ragamat
sed -e 's,\./ragamat,%{_bindir}/stk-ragamat,' -e '1i#! /bin/sh' \
  -i projects/ragamatic/Raga
cp -p projects/ragamatic/Raga %{buildroot}%{_datadir}/stk/ragamatic

cp -pr projects/eguitar/tcl %{buildroot}%{_datadir}/stk/eguitar
cp -pr projects/eguitar/scores %{buildroot}%{_datadir}/stk/eguitar
cp -p projects/eguitar/eguitar %{buildroot}%{_bindir}/stk-eguitar
sed -e 's,\./eguitar,%{_bindir}/stk-eguitar,' -e '1i#! /bin/sh' \
  -i projects/eguitar/ElectricGuitar
cp -p projects/eguitar/ElectricGuitar %{buildroot}%{_datadir}/stk/eguitar

# fix encoding
iconv -f iso-8859-1 -t utf-8 doc/doxygen/index.txt \
  -o doc/doxygen/index.txt.tmp
mv doc/doxygen/index.txt.tmp doc/doxygen/index.txt

# fix symlinks
symlinks -crv %{buildroot}

# remove .a files
rm -f %{buildroot}%{_libdir}/libstk.a

# finally, fix permissions
chmod -R u=rwX,go=rX %{buildroot}


%changelog
* Mon Jun 03 2013 Giovanni Mariani <mc2374@mclink.it> 4.4.4-1
- Import stk in Rosa 2012.1 from a Fedora package
- Provided a library package along with the -devel and -demos ones
- Added S100 to silence useless rpmlint warnings and errors