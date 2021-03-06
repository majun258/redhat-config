# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

%global src_pkg_name kernel-pegas
%global bin_pkg_name kernel
%global bin_suffix_name %{nil}

Summary: The Linux kernel

# % define buildid .local

# For a kernel released for public testing, released_kernel should be 1.
# For internal testing builds during development, it should be 0.
%global released_kernel 0

%global distro_build 4

%define rpmversion 4.11.0
%define pkgrelease 4.el7.lpcv2

# allow pkg_release to have configurable %{?dist} tag
%define specrelease 4%{?dist}.lpcv2

%define pkg_release %{specrelease}%{?buildid}

# The kernel tarball/base version
%define rheltarball %{rpmversion}-%{pkgrelease}

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks.

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them.
#
# kernel
%define with_default   %{?_without_default:   0} %{?!_without_default:   1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# tools
%define with_tools     %{?_without_tools:     0} %{?!_without_tools:     1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# kernel-kdump (only for s390x)
%define with_kdump     %{?_without_kdump:     0} %{?!_without_kdump:     0}
# kernel-bootwrapper (for creating zImages from kernel + initrd)
%define with_bootwrapper %{?_without_bootwrapper: 0} %{?!_without_bootwrapper: 0}
# kernel-abi-whitelists
%define with_kernel_abi_whitelists %{?_with_kernel_abi_whitelists: 0} %{?!_with_kernel_abi_whitelists: 1}

# In RHEL, we always want the doc build failing to build to be a failure,
# which means settings this to false.
%define doc_build_fail false

# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}

# Control whether we perform a compat. check against published ABI.
%define with_kabichk   %{?_without_kabichk:   0} %{?!_without_kabichk:   1}

# should we do C=1 builds with sparse
%define with_sparse    %{?_with_sparse:       1} %{?!_with_sparse:       0}

# Cross compile requested?
%define with_cross    %{?_with_cross:         1} %{?!_with_cross:        0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'. RHEL only ever does 1.
%define debugbuildsenabled 1

%define with_gcov %{?_with_gcov: 1} %{?!_with_gcov: 0}

# turn off debug kernel and kabichk for gcov builds
%if %{with_gcov}
%define with_debug 0
%define with_kabichk 0
%endif

%define make_target bzImage

# Kernel Version Release + Arch -> KVRA
%define KVRA %{version}-%{release}.%{_target_cpu}
%define hdrarch %{_target_cpu}
%define asmarch %{_target_cpu}
%define cross_target %{_target_cpu}

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# if requested, only build base kernel
%if %{with_baseonly}
%define with_debug 0
%define with_kdump 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%define with_default 0
%define with_kdump 0
%define with_tools 0
%define with_perf 0
%endif

# These arches install vdso/ directories.
%define vdso_arches aarch64 ppc64le s390x x86_64

# Overrides for generic default options

# only build debug kernel on architectures below
%ifnarch aarch64 ppc64le s390x x86_64
%define with_debug 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%define with_kernel_abi_whitelists 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_default 0
%define with_headers 0
%define with_tools 0
%define with_perf 0
%define all_arch_configs %{src_pkg_name}-%{version}-*.config
%endif

# sparse blows up on ppc*
%ifarch ppc64 ppc64le ppc
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch aarch64
%define asmarch arm64
%define hdrarch arm64
%define all_arch_configs %{src_pkg_name}-%{version}-aarch64*.config
%define make_target Image.gz
%define kernel_image arch/arm64/boot/Image.gz
%define image_install_path boot
%endif

%ifarch i686
%define asmarch x86
%define hdrarch i386
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs %{src_pkg_name}-%{version}-x86_64*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch ppc
%define asmarch powerpc
%define hdrarch powerpc
%endif

%ifarch ppc64 ppc64le
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs %{src_pkg_name}-%{version}-ppc64*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define with_bootwrapper 1
%define cross_target powerpc64
%define kcflags -O3
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs %{src_pkg_name}-%{version}-s390x*.config
%define image_install_path boot
%define kernel_image arch/s390/boot/bzImage
%define with_tools 0
%define with_kdump 1
%endif

#cross compile make
%if %{with_cross}
%define cross_opts CROSS_COMPILE=%{cross_target}-linux-gnu-
%define with_perf 0
%define with_tools 0
%endif

# Should make listnewconfig fail if there's config options
# printed out?
%define listnewconfig_fail 1

# We only build kernel headers package on the following, for being able to do
# builds with a different bit length (eg. 32-bit build on a 64-bit environment).
# Do not remove them from ExclusiveArch tag below
%define nobuildarches i686 ppc s390

%ifarch %nobuildarches
%define with_bootwrapper 0
%define with_default 0
%define with_debug 0
%define with_debuginfo 0
%define with_kdump 0
%define with_tools 0
%define with_perf 0
%define _enable_debug_packages 0
%endif

# Architectures we build tools/cpupower on
%define cpupowerarchs aarch64 ppc64le x86_64

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2, device-mapper-libs < 1.02.63-2, mdadm < 3.2.1-5

#
# Then a series of requirements that are distribution specific, either
# because we add patches for something, or the older versions have
# problems with the newer kernel or lack certain things that make
# integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3, xfsprogs < 4.3.0, kmod < 20-9

# We moved the drm include files into kernel headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools >= 3.16-2, initscripts >= 8.11.1-1, grubby >= 8.28-2
%define initrd_prereq  dracut >= 033-283

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:.%{1}}\
Provides: kernel-drm = 4.3.0\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-modeset = 1\
Provides: kernel-uname-r = %{KVRA}%{?1:.%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): linux-firmware >= 20160615-46\
Requires(post): %{_sbindir}/new-kernel-pkg\
Requires(post): system-release\
Requires(preun): %{_sbindir}/new-kernel-pkg\
Conflicts: %{kernel_dot_org_conflicts}\
Conflicts: %{package_conflicts}\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}

Name: %{src_pkg_name}
Group: System Environment/Kernel
License: GPLv2
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# Some architectures need a different headers version for user space builds with
# a different bit length environment (eg. 32-bit user space build on 64-bit).
# For architectures we support, where we must provide a compatible kernel-headers
# package, don't exclude them in ExclusiveArch below, but add them to
# %%nobuildarches (above) instead. Example: if we support x86_64, we must build
# the i686 (32-bit) headers and provide a package with them
ExclusiveArch: aarch64 i686 noarch ppc ppc64le s390 s390x x86_64
ExclusiveOS: Linux

#
# List the packages used during the kernel build
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: xz, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config >= 9.1.0-55
BuildRequires: hostname, net-tools, bc
BuildRequires: xmlto, asciidoc
BuildRequires: openssl openssl-devel
BuildRequires: hmaccalc
BuildRequires: python-devel, newt-devel, perl(ExtUtils::Embed)
%ifarch x86_64
BuildRequires: pesign >= 0.109-4
%endif
%if %{with_sparse}
BuildRequires: sparse >= 0.4.1
%endif
%if %{with_perf}
BuildRequires: elfutils-devel zlib-devel binutils-devel bison
BuildRequires: audit-libs-devel
%ifnarch s390 s390x
BuildRequires: numactl-devel
%endif
%endif
%if %{with_tools}
BuildRequires: pciutils-devel gettext ncurses-devel
%endif
%if %{with_debuginfo}
# Fancy new debuginfo generation introduced in Fedora 8/RHEL 6.
# The -r flag to find-debuginfo.sh invokes eu-strip --reloc-debug-sections
# which reduces the number of relocations in kernel module .ko.debug files and
# was introduced with rpm 4.9 and elfutils 0.153.
BuildRequires: rpm-build >= 4.9.0-1, elfutils >= 0.153-1
%define debuginfo_args --strict-build-id -r
%endif
%ifarch s390x
# required for zfcpdump
BuildRequires: glibc-static
%endif

Source0: linux-%{rpmversion}-%{pkgrelease}.tar.xz

Source1: Makefile.common

Source10: sign-modules
%define modsign_cmd %{SOURCE10}
Source11: x509.genkey
Source12: extra_certificates
%if %{?released_kernel}
Source13: securebootca.cer
Source14: secureboot.cer
%define pesign_name redhatsecureboot301
%else
Source13: redhatsecurebootca2.cer
Source14: redhatsecureboot003.cer
%define pesign_name redhatsecureboot003
%endif
Source15: rheldup3.x509
Source16: rhelkpatch1.x509

Source18: check-kabi

Source20: Module.kabi_x86_64
Source21: Module.kabi_ppc64le
Source22: Module.kabi_aarch64
Source23: Module.kabi_s390x

Source25: kernel-abi-whitelists-%{distro_build}.tar.bz2

Source50: %{src_pkg_name}-%{version}-x86_64.config
Source51: %{src_pkg_name}-%{version}-x86_64-debug.config

# Source60: %{src_pkg_name}-%{version}-ppc64.config
# Source61: %{src_pkg_name}-%{version}-ppc64-debug.config
Source62: %{src_pkg_name}-%{version}-ppc64le.config
Source63: %{src_pkg_name}-%{version}-ppc64le-debug.config

Source70: %{src_pkg_name}-%{version}-s390x.config
Source71: %{src_pkg_name}-%{version}-s390x-debug.config
Source72: %{src_pkg_name}-%{version}-s390x-kdump.config

Source80: %{src_pkg_name}-%{version}-aarch64.config
Source81: %{src_pkg_name}-%{version}-aarch64-debug.config

# Sources for kernel tools
Source2000: cpupower.service
Source2001: cpupower.config

# empty final patch to facilitate testing of kernel patches
Patch999999: linux-kernel-test.patch

BuildRoot: %{_tmppath}/%{src_pkg_name}-%{KVRA}-root

%description
The %{src_pkg_name} package contains the Linux kernel sources. The Linux kernel
is the core of any Linux operating system.  The kernel handles the basic
functions of the operating system: memory allocation, process allocation, device
input and output, etc.


%package -n %{bin_pkg_name}
Summary: The Linux kernel
Group: System Environment/Kernel
%kernel_reqprovconf

%description -n %{bin_pkg_name}
The %{bin_pkg_name} package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions of the operating
system: memory allocation, process allocation, device input and output, etc.


%package -n %{bin_pkg_name}-doc
Summary: Various documentation bits found in the kernel source
Group: Documentation
AutoReqProv: no
%description -n %{bin_pkg_name}-doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.


%package -n %{bin_pkg_name}-headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description -n %{bin_pkg_name}-headers
%{bin_pkg_name}-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package -n %{bin_pkg_name}-bootwrapper
Summary: Boot wrapper files for generating combined kernel + initrd images
Group: Development/System
Requires: gzip binutils
%description -n %{bin_pkg_name}-bootwrapper
%{bin_pkg_name}-bootwrapper contains the wrapper code which makes bootable "zImage"
files combining both kernel and initial ramdisk.

%package -n %{bin_pkg_name}-debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{bin_pkg_name}-debuginfo packages
Group: Development/Debug
%description -n %{bin_pkg_name}-debuginfo-common-%{_target_cpu}
This package is required by %{bin_pkg_name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%if %{with_perf}
%package -n perf%{?bin_suffix:-%{bin_suffix}}
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
%description -n perf%{?bin_suffix:-%{bin_suffix}}
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%package -n perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
Summary: Debug information for package perf
Group: Development/Debug
Requires: %{bin_pkg_name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
This package provides debug information for the perf package.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|XXX' -o perf-debuginfo.list}

%package -n python-perf%{?bin_suffix:-%{bin_suffix}}
Summary: Python bindings for apps which will manipulate perf events
Group: Development/Libraries
%description -n python-perf%{?bin_suffix:-%{bin_suffix}}
The python-perf%{?bin_suffix:-%{bin_suffix}} package contains a module that permits applications
written in the Python programming language to use the interface
to manipulate perf events.

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%package -n python-perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
Summary: Debug information for package perf python bindings
Group: Development/Debug
Requires: %{bin_pkg_name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n python-perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
This package provides debug information for the perf python bindings.

# the python_sitearch macro should already be defined from above
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{python_sitearch}/perf.so(\.debug)?|XXX' -o python-perf-debuginfo.list}


%endif # with_perf

%if %{with_tools}

%package -n %{bin_pkg_name}-tools
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:2.0
Requires: %{bin_pkg_name}-tools-libs = %{version}-%{release}
%description -n %{bin_pkg_name}-tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package -n %{bin_pkg_name}-tools-libs
Summary: Libraries for the %{bin_pkg_name}-tools
Group: Development/System
License: GPLv2
%description -n %{bin_pkg_name}-tools-libs
This package contains the libraries built from the tools/ directory
from the kernel source.

%package -n %{bin_pkg_name}-tools-libs-devel
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Requires: %{bin_pkg_name}-tools = %{version}-%{release}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
Requires: %{bin_pkg_name}-tools-libs = %{version}-%{release}
%description -n %{bin_pkg_name}-tools-libs-devel
This package contains the development files for the tools/ directory from
the kernel source.

%package -n %{bin_pkg_name}-tools-debuginfo
Summary: Debug information for package %{bin_pkg_name}-tools
Group: Development/Debug
Requires: %{bin_pkg_name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n %{bin_pkg_name}-tools-debuginfo
This package provides debug information for package %{bin_pkg_name}-tools.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|.*%%{_bindir}/tmon(\.debug)?|XXX' -o tools-debuginfo.list}

%endif # with_tools

%if %{with_gcov}
%package -n %{bin_pkg_name}-gcov
Summary: gcov graph and source files for coverage data collection.
Group: Development/System
%description -n %{bin_pkg_name}-gcov
kernel-gcov includes the gcov graph and source files for gcov coverage collection.
%endif

%package -n %{bin_pkg_name}-abi-whitelists
Summary: The Red Hat Enterprise Linux kernel ABI symbol whitelists
Group: System Environment/Kernel
AutoReqProv: no
%description -n %{bin_pkg_name}-abi-whitelists
The kABI package contains information pertaining to the Red Hat Enterprise
Linux kernel ABI, including lists of kernel symbols that are needed by
external Linux kernel modules, and a yum plugin to aid enforcement.

#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
%define kernel_debuginfo_package() \
%package -n %{bin_pkg_name}-%{?1:%{1}-}debuginfo\
Summary: Debug information for package %{bin_pkg_name}%{?1:-%{1}}\
Group: Development/Debug\
Requires: %{bin_pkg_name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{bin_pkg_name}-%{?1:%{1}-}debuginfo-%{_target_cpu} = %{version}-%{release}\
AutoReqProv: no\
%description -n %{bin_pkg_name}-%{?1:%{1}-}debuginfo\
This package provides debug information for package %{bin_pkg_name}%{?1:-%{1}}.\
This is required to use SystemTap with %{bin_pkg_name}%{?1:-%{1}}-%{KVRA}.\
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '/.*/%%{KVRA}%{?1:\.%{1}}/.*|/.*%%{KVRA}%{?1:\.%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package -n %{bin_pkg_name}-%{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: %{bin_pkg_name}-%{?1:%{1}-}devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel-uname-r = %{KVRA}%{?1:.%{1}}\
AutoReqProv: no\
Requires(pre): /usr/bin/find\
Requires: perl\
%description -n %{bin_pkg_name}-%{?1:%{1}-}devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package -n %{bin_pkg_name}-%1\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
%kernel_reqprovconf\
%{expand:%%kernel_devel_package %1 %{!?-n:%1}%{?-n:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %1}\
%{nil}


# First the auxiliary packages of the main kernel package.
%kernel_devel_package
%kernel_debuginfo_package


# Now, each variant package.

%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description -n %{bin_pkg_name}-debug
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.

%define variant_summary A minimal Linux kernel compiled for crash dumps
%kernel_variant_package kdump
%description -n %{bin_pkg_name}-kdump
This package includes a kdump version of the Linux kernel. It is
required only on machines which will use the kexec-based kernel crash dump
mechanism.

%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_default}
echo "Cannot build --with baseonly, default kernel build is disabled"
exit 1
%endif
%endif

# more sanity checking; do it quietly
if [ "%{patches}" != "%%{patches}" ] ; then
  for patch in %{patches} ; do
    if [ ! -f $patch ] ; then
      echo "ERROR: Patch  ${patch##/*/}  listed in specfile but is missing"
      exit 1
    fi
  done
fi 2>/dev/null

patch_command='patch -p1 -F1 -s'
ApplyPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME}.spec ; then
    if [ "${patch:0:8}" != "patch-3." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz) gunzip < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *) $patch_command ${1+"$@"} < "$RPM_SOURCE_DIR/$patch" ;;
  esac
}

# don't apply patch if it's empty
ApplyOptionalPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  local C=$(wc -l $RPM_SOURCE_DIR/$patch | awk '{print $1}')
  if [ "$C" -gt 9 ]; then
    ApplyPatch $patch ${1+"$@"}
  fi
}

%setup -q -n %{src_pkg_name}-%{rheltarball} -c
mv linux-%{rheltarball} linux-%{KVRA}
cd linux-%{KVRA}

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/%{src_pkg_name}-%{version}-*.config .

ApplyOptionalPatch linux-kernel-test.patch

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

if [ -L configs ]; then
	rm -f configs
	mkdir configs
fi

# Remove configs not for the buildarch
for cfg in %{src_pkg_name}-%{version}-*.config; do
  if [ `echo %{all_arch_configs} | grep -c $cfg` -eq 0 ]; then
    rm -f $cfg
  fi
done

%if !%{debugbuildsenabled}
rm -f %{src_pkg_name}-%{version}-*debug.config
%endif

# enable GCOV kernel config options if gcov is on
%if %{with_gcov}
for i in *.config
do
  sed -i 's/# CONFIG_GCOV_KERNEL is not set/CONFIG_GCOV_KERNEL=y\nCONFIG_GCOV_PROFILE_ALL=y\n/' $i
done
%endif

# now run oldconfig over all the config files
for i in *.config
do
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
  make %{?cross_opts} ARCH=$Arch listnewconfig | grep -E '^CONFIG_' >.newoptions || true
%if %{listnewconfig_fail}
  if [ -s .newoptions ]; then
    cat .newoptions
    exit 1
  fi
%endif
  rm -f .newoptions
  make %{?cross_opts} ARCH=$Arch oldnoconfig
  echo "# $Arch" > configs/$i
  cat .config >> configs/$i
done
# end of kernel config
%endif

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

# remove unnecessary SCM files
find . -name .gitignore -exec rm -f {} \; >/dev/null

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

%if %{with_debuginfo}
# This override tweaks the kernel makefiles so that we run debugedit on an
# object before embedding it.  When we later run find-debuginfo.sh, it will
# run debugedit again.  The edits it does change the build ID bits embedded
# in the stripped object, but repeating debugedit is a no-op.  We do it
# beforehand to get the proper final build ID bits into the embedded image.
# This affects the vDSO images in vmlinux, and the vmlinux image in bzImage.
export AFTER_LINK='sh -xc "/usr/lib/rpm/debugedit -b $$RPM_BUILD_DIR -d /usr/src/debug -i $@ > $@.id"'
%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$3
    InstallName=${4:-vmlinuz}

    # Pick the right config file for the kernel we're building
    Config=%{src_pkg_name}-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}.config
    DevelDir=/usr/src/kernels/%{KVRA}${Flavour:+.${Flavour}}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{KVRA}${Flavour:+.${Flavour}}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}${Flavour:+.${Flavour}}/" Makefile

    # and now to start the build process

    make %{?cross_opts} -s mrproper

    cp %{SOURCE11} ./certs	# x509.genkey
    cp %{SOURCE12} ./certs	# extra_certificates
    cp %{SOURCE15} ./certs	# rheldup3.x509
    cp %{SOURCE16} ./certs	# rhelkpatch1.x509

    cp configs/$Config .config

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

%ifarch s390x
    if [ "$Flavour" == "kdump" ]; then
        pushd arch/s390/boot
        gcc -static -o zfcpdump zfcpdump.c
        popd
    fi
%endif

    make -s %{?cross_opts} ARCH=$Arch oldnoconfig >/dev/null
    make -s %{?cross_opts} ARCH=$Arch V=1 %{?_smp_mflags} KCFLAGS="%{?kcflags}" WITH_GCOV="%{?with_gcov}" $MakeTarget %{?sparse_mflags}

    if [ "$Flavour" != "kdump" ]; then
        make -s %{?cross_opts} ARCH=$Arch V=1 %{?_smp_mflags} KCFLAGS="%{?kcflags}" WITH_GCOV="%{?with_gcov}" modules %{?sparse_mflags} || exit 1
    fi

    # Start installing the results
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/boot
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
    fi
# EFI SecureBoot signing, x86_64-only
%ifarch x86_64
    %pesign -s -i $KernelImage -o $KernelImage.signed -a certs/%{SOURCE13} -c certs/%{SOURCE14} -n %{pesign_name}
    mv $KernelImage.signed $KernelImage
%endif
    $CopyKernel $KernelImage $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer

    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/kernel
    if [ "$Flavour" != "kdump" ]; then
        # Override $(mod-fw) because we don't want it to install any firmware
        # we'll get it from the linux-firmware package and we don't want conflicts
        make -s %{?cross_opts} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=
%if %{with_gcov}
	# install gcov-needed files to $BUILDROOT/$BUILD/...:
	#   gcov_info->filename is absolute path
	#   gcno references to sources can use absolute paths (e.g. in out-of-tree builds)
	#   sysfs symlink targets (set up at compile time) use absolute paths to BUILD dir
	find . \( -name '*.gcno' -o -name '*.[chS]' \) -exec install -D '{}' "$RPM_BUILD_ROOT/$(pwd)/{}" \;
%endif
    fi
%ifarch %{vdso_arches}
    make -s %{?cross_opts} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
    if [ ! -s ldconfig-kernel.conf ]; then
      echo > ldconfig-kernel.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-kernel.conf $RPM_BUILD_ROOT/etc/ld.so.conf.d/%{bin_pkg_name}-$KernelVer.conf
%endif

    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    (cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
    # dirs for additional modules per module-init-tools, kbuild/modules.txt
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi

    # create the kABI metadata for use in packaging
    # NOTENOTE: the name symvers is used by the rpm backend
    # NOTENOTE: to discover and run the /usr/lib/rpm/fileattrs/kabi.attr
    # NOTENOTE: script which dynamically adds exported kernel symbol
    # NOTENOTE: checksums to the rpm metadata provides list.
    # NOTENOTE: if you change the symvers name, update the backend too
    echo "**** GENERATING kernel ABI metadata ****"
    gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz

%if %{with_kabichk}
    echo "**** kABI checking is enabled in kernel SPEC file. ****"
    chmod 0755 $RPM_SOURCE_DIR/check-kabi
    if [ -e $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        rm $RPM_BUILD_ROOT/Module.kabi # for now, don't keep it around.
    else
        echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif

    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
%ifarch ppc64 ppc64le
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
%ifarch aarch64
    # some arch/arm64 header files refer to arch/arm, so include them too
    cp -a --parents arch/arm/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    # include/trace/events/wbt.h uses blk-{wbt,stat}.h private kernel headers,
    # and systemtap uses wbt.h when we run a script which uses wbt:* trace points
    cp block/blk-{wbt,stat}.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/block/

    # copy objtool for kernel-devel (needed for building external modules)
    if grep -q CONFIG_STACK_VALIDATION=y .config; then
      mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool
      cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool
    fi

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/autoconf.h
    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{with_debuginfo}
    if test -s vmlinux.id; then
      cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id
    else
      echo >&2 "*** ERROR *** no vmlinux build ID! ***"
      exit 1
    fi

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
      LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      if [ ! -z "$3" ]; then
        sed -r -e "/^($3)\$/d" -i $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      fi
    }

    collect_modules_list networking 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt2x00(pci|usb)_probe|register_netdevice'
    collect_modules_list block 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' 'pktcdvd.ko|dm-mod.ko'
    collect_modules_list drm 'drm_open|drm_init'
    collect_modules_list modesetting 'drm_crtc_init'

    # detect missing or incorrect license tags
    rm -f modinfo
    while read i
    do
      echo -n "${i#$RPM_BUILD_ROOT/lib/modules/$KernelVer/} " >> modinfo
      /sbin/modinfo -l $i >> modinfo
    done < modnames

    grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' modinfo && exit 1

    rm -f modinfo modnames

    # Save off the .tmp_versions/ directory.  We'll use it in the
    # __debug_install_post macro below to sign the right things
    # Also save the signing keys so we actually sign the modules with the
    # right key.
    cp -r .tmp_versions .tmp_versions.sign${Flavour:+.${Flavour}}
    cp certs/signing_key.pem signing_key.pem.sign${Flavour:+.${Flavour}}
    cp certs/signing_key.x509 signing_key.x509.sign${Flavour:+.${Flavour}}

    # remove files that will be auto generated by depmod at rpm -i time
    for i in alias alias.bin builtin.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap softdep devname
    do
      rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
    done

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir
    ln -sf $DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    # prune junk from kernel-devel
    find $RPM_BUILD_ROOT/usr/src/kernels -name ".*.cmd" -exec rm -f {} \;
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}

cd linux-%{KVRA}

%if %{with_default}
BuildKernel %make_target %kernel_image
%endif

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_kdump}
BuildKernel %make_target %kernel_image kdump
%endif

%global perf_make make %{?_smp_mflags} -C tools/perf -s V=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_STRLCPY=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 prefix=%{_prefix} lib=%{_lib}
%if %{with_perf}
# perf
%{perf_make} all
%{perf_make} man || %{doc_build_fail}
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
make %{?cross_opts} %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    make %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch x86_64
   pushd tools/power/x86/x86_energy_perf_policy/
   make
   popd
   pushd tools/power/x86/turbostat
   make
   popd
%endif #turbostat/x86_energy_perf_policy
%endif
pushd tools
make tmon
popd
%endif

%if %{with_doc}
# Make the HTML and man pages.
make htmldocs mandocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

# In the modsign case, we do 3 things.  1) We check the "flavour" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that flavour.  3) We
# grab the arch and invoke 'make modules_sign' and the mod-extra-sign.sh
# commands to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.
#
# Finally, pick a module at random and check that it's signed and fail the build
# if it isn't.

%define __modsign_install_post \
  if [ "%{with_debug}" -ne "0" ]; then \
    Arch=`head -1 configs/%{src_pkg_name}-%{version}-%{_target_cpu}-debug.config | cut -b 3-` \
    rm -rf .tmp_versions \
    mv .tmp_versions.sign.debug .tmp_versions \
    mv signing_key.pem.sign.debug signing_key.pem \
    mv signing_key.x509.sign.debug signing_key.x509 \
    %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KVRA}.debug || exit 1 \
  fi \
    if [ "%{with_default}" -ne "0" ]; then \
    Arch=`head -1 configs/%{src_pkg_name}-%{version}-%{_target_cpu}.config | cut -b 3-` \
    rm -rf .tmp_versions \
    mv .tmp_versions.sign .tmp_versions \
    mv signing_key.pem.sign signing_key.pem \
    mv signing_key.x509.sign signing_key.x509 \
    %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KVRA} || exit 1 \
  fi \
%{nil}

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{with_debuginfo}

%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh %{debuginfo_args} %{_builddir}/%{?buildsubdir}\
%{nil}

%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list -n %{bin_pkg_name}-debuginfo-common-%{_target_cpu}
%defattr(-,root,root)
%endif

%endif

#
# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
#
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}}\
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__modsign_install_post}

###
### install
###

%install

cd linux-%{KVRA}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{rpmversion}
man9dir=$RPM_BUILD_ROOT%{_datadir}

# copy the source over
mkdir -p $docdir
tar -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $docdir

# Install man pages for the kernel API.
mkdir -p $man9dir/man/man9
make INSTALL_MAN_PATH=$man9dir installmandocs
ls $man9dir/man/man9 | grep -q '' || > $man9dir/man/man9/BROKEN
%endif # with_doc

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel headers
make %{?cross_opts} ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Do headers_check but don't die if it fails.
make %{?cross_opts} ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_check > hdrwarnings.txt || :
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   # exit 1
fi

find $RPM_BUILD_ROOT/usr/include \( -name .install -o -name .check -o -name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

%endif

%if %{with_kernel_abi_whitelists}
# kabi directory
INSTALL_KABI_PATH=$RPM_BUILD_ROOT/lib/modules/
mkdir -p $INSTALL_KABI_PATH

# install kabi releases directories
tar xjvf %{SOURCE25} -C $INSTALL_KABI_PATH
%endif  # with_kernel_abi_whitelists

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install
# remove the 'trace' symlink.
rm -f $RPM_BUILD_ROOT/%{_bindir}/trace

# perf-python extension
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages (note: implicit rpm magic compresses them later)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT try-install-man || %{doc_build_fail}
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
make -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2000} %{buildroot}%{_unitdir}/cpupower.service
install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
   mkdir -p %{buildroot}%{_mandir}/man8
   pushd tools/power/x86/x86_energy_perf_policy
   make DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/turbostat
   make DESTDIR=%{buildroot} install
   popd
%endif #turbostat/x86_energy_perf_policy
pushd tools/thermal/tmon
make INSTALL_ROOT=%{buildroot} install
popd
%endif

%endif

%if %{with_bootwrapper}
make %{?cross_opts} ARCH=%{hdrarch} DESTDIR=$RPM_BUILD_ROOT bootwrapper_install WRAPPER_OBJDIR=%{_libdir}/kernel-wrapper WRAPPER_DTSDIR=%{_libdir}/kernel-wrapper/dts
%endif

%if %{with_doc}
# Red Hat UEFI Secure Boot CA cert, which can be used to authenticate the kernel
mkdir -p $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/%{rpmversion}-%{pkgrelease}
install -m 0644 %{SOURCE13} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/%{rpmversion}-%{pkgrelease}/kernel-signing-ca.cer
%endif

###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT

###
### scripts
###

%if %{with_tools}
%post -n %{bin_pkg_name}-tools
/sbin/ldconfig

%postun -n %{bin_pkg_name}-tools
/sbin/ldconfig
%endif

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
#
%define kernel_devel_post() \
%{expand:%%post -n %{bin_pkg_name}-%{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]\
then\
    (cd /usr/src/kernels/%{KVRA}%{?1:.%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*.%{?dist}.*/$f $f\
     done)\
fi\
%{nil}


# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans -n %{bin_pkg_name}%{?1:-%{1}}}\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --add-kernel %{KVRA}%{?1:.%{1}} || exit $?\
fi\
%{_sbindir}/new-kernel-pkg --package %{bin_pkg_name}%{?-v:-%{-v*}} --mkinitrd --dracut --depmod --update %{KVRA}%{?-v:.%{-v*}} || exit $?\
%{_sbindir}/new-kernel-pkg --package %{bin_pkg_name}%{?1:-%{1}} --rpmposttrans %{KVRA}%{?1:.%{1}} || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post -n %{bin_pkg_name}%{?-v:-%{-v*}}}\
%{-r:\
if [ `uname -i` == "x86_64" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{expand:\
%{_sbindir}/new-kernel-pkg --package %{bin_pkg_name}%{?-v:-%{-v*}} --install %{KVRA}%{?-v:.%{-v*}} || exit $?\
}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun -n %{bin_pkg_name}%{?1:-%{1}}}\
%{_sbindir}/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVRA}%{?1:.%{1}} || exit $?\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --remove-kernel %{KVRA}%{?1:.%{1}} || exit $?\
fi\
%{nil}

%kernel_variant_preun
%kernel_variant_post 

%kernel_variant_preun debug
%kernel_variant_post -v debug

%ifarch s390x
%postun -n %{bin_pkg_name}-kdump
    # Create softlink to latest remaining kdump kernel.
    # If no more kdump kernel is available, remove softlink.
    if [ "$(readlink /boot/zfcpdump)" == "/boot/vmlinuz-%{KVRA}.kdump" ]
    then
        vmlinuz_next=$(ls /boot/vmlinuz-*.kdump 2> /dev/null | sort | tail -n1)
        if [ $vmlinuz_next ]
        then
            ln -sf $vmlinuz_next /boot/zfcpdump
        else
            rm -f /boot/zfcpdump
        fi
    fi

%post -n %{bin_pkg_name}-kdump
    ln -sf /boot/vmlinuz-%{KVRA}.kdump /boot/zfcpdump
%endif # s390x

###
### file lists
###

%if %{with_headers}
%files -n %{bin_pkg_name}-headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_bootwrapper}
%files -n %{bin_pkg_name}-bootwrapper
%defattr(-,root,root)
/usr/sbin/*
%{_libdir}/kernel-wrapper
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files -n %{bin_pkg_name}-doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}
%{_datadir}/man/man9/*
%{_datadir}/doc/kernel-keys/%{rpmversion}-%{pkgrelease}/kernel-signing-ca.cer
%dir %{_datadir}/doc/kernel-keys/%{rpmversion}-%{pkgrelease}
%dir %{_datadir}/doc/kernel-keys
%endif

%if %{with_kernel_abi_whitelists}
%files -n %{bin_pkg_name}-abi-whitelists
%defattr(-,root,root,-)
/lib/modules/kabi-*
%endif

%if %{with_perf}
%files -n perf%{?bin_suffix:-%{bin_suffix}}
%defattr(-,root,root)
%{_bindir}/perf
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_libdir}/traceevent
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%{_datadir}/perf-core/strace/groups
%{_datadir}/doc/perf-tip/tips.txt

%files -n python-perf%{?bin_suffix:-%{bin_suffix}}
%defattr(-,root,root)
%{python_sitearch}

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
%defattr(-,root,root)

%files -f python-perf-debuginfo.list -n python-perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
%defattr(-,root,root)
%endif
%endif

%if %{with_tools}
%files -n %{bin_pkg_name}-tools -f cpupower.lang
%defattr(-,root,root)
%ifarch %{cpupowerarchs}
%{_bindir}/cpupower
%ifarch x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%endif
%endif
%{_bindir}/tmon
%if %{with_debuginfo}
%files -f tools-debuginfo.list -n %{bin_pkg_name}-tools-debuginfo
%defattr(-,root,root)
%endif

%ifarch %{cpupowerarchs}
%files -n %{bin_pkg_name}-tools-libs
%defattr(-,root,root)
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1

%files -n %{bin_pkg_name}-tools-libs-devel
%defattr(-,root,root)
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%endif

%endif # with_tools

%if %{with_gcov}
%ifarch x86_64 s390x ppc64 ppc64le
%files -n %{bin_pkg_name}-gcov
%defattr(-,root,root)
%{_builddir}
%endif
%endif

# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{1}\
%{expand:%%files -n %{bin_pkg_name}%{?2:-%{2}}}\
%defattr(-,root,root)\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVRA}%{?2:.%{2}}\
/%{image_install_path}/.vmlinuz-%{KVRA}%{?2:.%{2}}.hmac \
%attr(600,root,root) /boot/System.map-%{KVRA}%{?2:.%{2}}\
/boot/symvers-%{KVRA}%{?2:.%{2}}.gz\
/boot/config-%{KVRA}%{?2:.%{2}}\
%dir /lib/modules/%{KVRA}%{?2:.%{2}}\
/lib/modules/%{KVRA}%{?2:.%{2}}/kernel\
/lib/modules/%{KVRA}%{?2:.%{2}}/build\
/lib/modules/%{KVRA}%{?2:.%{2}}/source\
/lib/modules/%{KVRA}%{?2:.%{2}}/extra\
/lib/modules/%{KVRA}%{?2:.%{2}}/updates\
/lib/modules/%{KVRA}%{?2:.%{2}}/weak-updates\
%ifarch %{vdso_arches}\
/lib/modules/%{KVRA}%{?2:.%{2}}/vdso\
/etc/ld.so.conf.d/%{bin_pkg_name}-%{KVRA}%{?2:.%{2}}.conf\
%endif\
/lib/modules/%{KVRA}%{?2:.%{2}}/modules.*\
%ghost /boot/initramfs-%{KVRA}%{?2:.%{2}}.img\
%{expand:%%files -n %{bin_pkg_name}-%{?2:%{2}-}devel}\
%defattr(-,root,root)\
/usr/src/kernels/%{KVRA}%{?2:.%{2}}\
%if %{with_debuginfo}\
%ifnarch noarch\
%{expand:%%files -f debuginfo%{?2}.list -n %{bin_pkg_name}-%{?2:%{2}-}debuginfo}\
%defattr(-,root,root)\
%endif\
%endif\
%endif\
%{nil}

%kernel_variant_files %{with_default}
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_kdump} kdump

%changelog
* Thu May 25 2017 Jun ma <juma@redhat.com> [4.11.0-4.el7.lpcv2]
- hisi: lpc: ipmi: implement IPMI BT handlers based on the LPC in/out. (Wei Xu)
- hisi: lpc: ipmi: add the basic to build as a independent ko ("zhichang.yuan")
- irqchip/mbigen: Fix the clear register offset calculation (MaJun)
- irqchip/mbigen: Fix potential NULL dereferencing (Hanjun Guo)
- irqchip/mbigen: Fix memory mapping code (Hanjun Guo)
- irqchip/mbigen: Fix return value check in mbigen_device_probe() (Wei Yongjun)
- Fwd: patch for redhat test ("majun (Euler7)")

* Mon May 22 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-4.el7]
- [misc] cxl: Enable PCI device IDs for future IBM CXL adapters (Steve Best) [1452796]
- [redhat] kconfig: PowerNV platform RTC driver for power 9 (Steve Best) [1452588]
- [powerpc] KVM: PPC: Book3S HV: Native usage of the XIVE interrupt controller (David Gibson) [1396118]
- [pci] Apply Cavium ACS quirk only to CN81xx/CN83xx/CN88xx devices (Robert Richter) [1451727]
- [redhat] kconfig: Enable this driver to get read/write support I2C EEPROMs for power 9 (Steve Best) [1451680]
- [tools] perf trace: Handle unpaired raw_syscalls:sys_exit event (Jiri Olsa) [1441286]
- [redhat] Enable Qualcomm IPMI and EMAC drivers (Steve Ulrich) [1443724]
- [scsi] hisi_sas: controller reset for multi-bits ECC and AXI fatal errors (Zhou Wang) [1266303]
- [scsi] hisi_sas: fix NULL deference when TMF timeouts (Zhou Wang) [1266303]
- [scsi] hisi_sas: add v2 hw internal abort timeout workaround (Zhou Wang) [1266303]
- [scsi] hisi_sas: workaround SoC about abort timeout bug (Zhou Wang) [1266303]
- [scsi] hisi_sas: workaround a SoC SATA IO processing bug (Zhou Wang) [1266303]
- [scsi] hisi_sas: workaround STP link SoC bug (Zhou Wang) [1266303]
- [scsi] hisi_sas: fix SATA dependency (Zhou Wang) [1266303]
- [scsi] hisi_sas: add missing break in switch statement (Zhou Wang) [1266303]
- [scsi] hisi_sas: add is_sata_phy_v2_hw() (Zhou Wang) [1266303]
- [scsi] hisi_sas: use dev_is_sata to identify SATA or SAS disk (Zhou Wang) [1266303]
- [scsi] hisi_sas: check hisi_sas_lu_reset() error message (Zhou Wang) [1266303]
- [scsi] hisi_sas: release SMP slot in lldd_abort_task (Zhou Wang) [1266303]
- [scsi] hisi_sas: add hisi_sas_clear_nexus_ha() (Zhou Wang) [1266303]
- [scsi] hisi_sas: rename hisi_sas_link_timeout_enable/disable_link (Zhou Wang) [1266303]
- [scsi] hisi_sas: handle PHY UP+DOWN simultaneous irq (Zhou Wang) [1266303]
- [scsi] hisi_sas: some modifications to v2 hw reg init (Zhou Wang) [1266303]
- [scsi] hisi_sas: process error codes according to their priority (Zhou Wang) [1266303]
- [scsi] hisi_sas: remove task free'ing for timeouts (Zhou Wang) [1266303]
- [scsi] hisi_sas: fix some sas_task.task_state_lock locking (Zhou Wang) [1266303]
- [scsi] hisi_sas: free slots after hardreset (Zhou Wang) [1266303]
- [scsi] hisi_sas: check for SAS_TASK_STATE_ABORTED in slot complete (Zhou Wang) [1266303]
- [scsi] hisi_sas: hardreset for SATA disk in LU reset (Zhou Wang) [1266303]
- [scsi] hisi_sas: modify hisi_sas_abort_task() for SSP (Zhou Wang) [1266303]
- [scsi] hisi_sas: modify error handling for v2 hw (Zhou Wang) [1266303]
- [scsi] hisi_sas: only reset link for PHY_FUNC_LINK_RESET (Zhou Wang) [1266303]
- [scsi] hisi_sas: error hisi_sas_task_prep() when port down (Zhou Wang) [1266303]
- [scsi] hisi_sas: remove hisi_sas_port_deformed() (Zhou Wang) [1266303]
- [scsi] hisi_sas: add softreset function for SATA disk (Zhou Wang) [1266303]
- [scsi] hisi_sas: move PHY init to hisi_sas_scan_start() (Zhou Wang) [1266303]
- [scsi] hisi_sas: add controller reset (Zhou Wang) [1266303]
- [scsi] hisi_sas: add to_hisi_sas_port() (Zhou Wang) [1266303]
- [redhat] aarch64: configs: Enable HiSilicon SAS controller (Zhou Wang) [1266303]
- [netdrv] hns: fix ethtool_get_strings overflow in hns driver (Zhou Wang) [1266302]
- [netdrv] hns: support deferred probe when no mdio (Zhou Wang) [1266302]
- [netdrv] hns: support deferred probe when can not obtain irq (Zhou Wang) [1266302]
- [netdrv] hns: Some checkpatch.pl script & warning fixes (Zhou Wang) [1266302]
- [netdrv] hns: Avoid Hip06 chip TX packet line bug (Zhou Wang) [1266302]
- [netdrv] hns: Adjust the SBM module buffer threshold (Zhou Wang) [1266302]
- [netdrv] hns: Simplify the exception sequence in hns_ppe_init() (Zhou Wang) [1266302]
- [netdrv] hns: Optimise the code in hns_mdio_wait_ready() (Zhou Wang) [1266302]
- [netdrv] hns: Clean redundant code from hns_mdio.c file (Zhou Wang) [1266302]
- [netdrv] hns: Remove redundant mac table operations (Zhou Wang) [1266302]
- [netdrv] hns: Remove redundant mac_get_id() (Zhou Wang) [1266302]
- [netdrv] hns: Remove the redundant adding and deleting mac function (Zhou Wang) [1266302]
- [netdrv] hns: Correct HNS RSS key set function (Zhou Wang) [1266302]
- [netdrv] hns: Replace netif_tx_lock to ring spin lock (Zhou Wang) [1266302]
- [netdrv] hns: Fix to adjust buf_size of ring according to mtu (Zhou Wang) [1266302]
- [netdrv] hns: Optimize hns_nic_common_poll for better performance (Zhou Wang) [1266302]
- [netdrv] hns: bug fix of ethtool show the speed (Zhou Wang) [1266302]
- [netdrv] hns: Remove redundant memset during buffer release (Zhou Wang) [1266302]
- [netdrv] hns: Optimize the code for GMAC pad and crc Config (Zhou Wang) [1266302]
- [netdrv] hns: Modify GMAC init TX threshold value (Zhou Wang) [1266302]
- [netdrv] hns: Fix the implementation of irq affinity function (Zhou Wang) [1266302]
- [redhat] aarch64: configs: Enable HiSilicon HNS networking modules (Zhou Wang) [1266302]
- [iommu] aarch64: Set bypass mode per default (Robert Richter) [1437372]
- [iommu] arm-smmu: Return IOVA in iova_to_phys when SMMU is bypassed (Robert Richter) [1437372]
- [iommu] Print a message with the default domain type created (Robert Richter) [1437372]
- [iommu] Allow default domain type to be set on the kernel command line (Robert Richter) [1437372]
- [iommu] arm-smmu-v3: Install bypass STEs for IOMMU_DOMAIN_IDENTITY domains (Robert Richter) [1437372]
- [iommu] arm-smmu-v3: Make arm_smmu_install_ste_for_dev return void (Robert Richter) [1437372]
- [iommu] arm-smmu: Install bypass S2CRs for IOMMU_DOMAIN_IDENTITY domains (Robert Richter) [1437372]
- [iommu] arm-smmu: Restrict domain attributes to UNMANAGED domains (Robert Richter) [1437372]
- [edac] thunderx: Remove unused code (Robert Richter) [1243040]
- [edac] thunderx: Change LMC index calculation (Robert Richter) [1243040]
- [edac] thunderx: Fix L2C MCI interrupt disable (Robert Richter) [1243040]

* Mon May 15 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-3.el7]
- [arm64] redhat: crashkernel auto reservation code for ARM64 (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [firmware] efi/libstub/arm*: Set default address and size cells values for an empty dtb (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [documentation] dt: chosen properties for arm64 kdump (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [documentation] kdump: describe arm64 port (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] kdump: enable kdump in defconfig (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] kdump: provide /proc/vmcore file (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] kdump: add VMCOREINFO's for user-space tools (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] kdump: implement machine_crash_shutdown() (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] hibernate: preserve kdump image around hibernation (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] kdump: protect crash dump kernel memory (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mm: add set_memory_valid() (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] kdump: reserve memory for crash dump kernel (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] limit memory regions based on DT property, usable-memory-range (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [mm] memblock: add memblock_cap_memory_range() (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [mm] memblock: add memblock_clear_nomap() (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mm: set the contiguous bit for kernel mappings where appropriate (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mm: remove pointless map/unmap sequences when creating page tables (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: replace 'page_mappings_only' parameter with flags argument (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: add contiguous bit to sanity bug check (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: ignore debug_pagealloc for kernel segments (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: align alloc_init_pte prototype with pmd/pud versions (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: apply strict permissions to .init.text and .init.data (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: map .text as read-only from the outset (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] alternatives: apply boot time fixups via the linear mapping (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: move TLB maintenance from callers to create_mapping_late() (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [virt] arm: kvm: move kvm_vgic_global_state out of .text section (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [mm] Revert "memblock: add memblock_clear_nomap()" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [mm] Revert "memblock: add memblock_cap_memory_range()" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: limit memory regions based on DT property, usable-memory-range" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: kdump: reserve memory for crash dump kernel" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: mm: add set_memory_valid()" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: kdump: protect crash dump kernel memory" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: hibernate: preserve kdump image around hibernation" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: kdump: implement machine_crash_shutdown()" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: kdump: add VMCOREINFO's for user-space tools" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: kdump: provide /proc/vmcore file" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: kdump: enable kdump in defconfig" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [documentation] Revert "Documentation: kdump: describe arm64 port" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [documentation] Revert "Documentation: dt: chosen properties for arm64 kdump" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [firmware] Revert "efi/libstub/arm*: Set default address and size cells values for an empty dtb" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "redhat: crashkernel auto reservation code for ARM64" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [redhat] use installmandocs target to install kernel API man pages ("Herton R. Krzesinski") [1451051]
- [documentation] allow installing man pages to a user defined directory ("Herton R. Krzesinski") [1451051]
- [powerpc] perf: Add Power8 mem_access event to sysfs (Steve Best) [1368735]
- [powerpc] perf: Support to export SIERs bit in Power9 (Steve Best) [1368735]
- [powerpc] perf: Support to export SIERs bit in Power8 (Steve Best) [1368735]
- [powerpc] perf: Support to export MMCRA(TEC*) field to userspace (Steve Best) [1368735]
- [powerpc] perf: Export memory hierarchy info to user space (Steve Best) [1368735]
- [netdrv] i40e: only register client on iWarp-capable devices (Stefan Assmann) [1441817]
- [netdrv] i40e: close client on remove and shutdown (Stefan Assmann) [1441817]
- [netdrv] i40e: register existing client on probe (Stefan Assmann) [1441817]
- [netdrv] i40e: remove client instance on driver unload (Stefan Assmann) [1441817]
- [netdrv] i40e: fix RSS queues only operating on PF0 (Stefan Assmann) [1441817]
- [netdrv] i40e: initialize params before notifying of l2_param_changes (Stefan Assmann) [1441817]
- [netdrv] i40e: KISS the client interface (Stefan Assmann) [1441817]
- [netdrv] i40e: fix up recent proxy and wol bits for X722_SUPPORT (Stefan Assmann) [1441817]
- [netdrv] i40e: Acquire NVM lock before reads on all devices (Stefan Assmann) [1441817]
- [netdrv] drivers: net: xgene: Add workaround for errata 10GE_8/ENET_11 (Iyappan Subramanian) [1441795]
- [netdrv] drivers: net: xgene: Add workaround for errata 10GE_1 (Iyappan Subramanian) [1441795]
- [netdrv] drivers: net: xgene: Fix Rx checksum validation logic (Iyappan Subramanian) [1441795]
- [netdrv] drivers: net: xgene: Fix wrong logical operation (Iyappan Subramanian) [1441795]
- [netdrv] drivers: net: xgene: Fix hardware checksum setting (Iyappan Subramanian) [1441795]
- [netdrv] drivers: net: phy: xgene: Fix mdio write (Iyappan Subramanian) [1441795]
- [block] sg_io: introduce unpriv_sgio queue flag (Paolo Bonzini) [1394238]
- [block] sg_io: pass request_queue to blk_verify_command (Paolo Bonzini) [1394238]
- [redhat] aarch64: configs: Enable X-Gene Ethernet v2 (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Fix error return code in xge_mdio_config() (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Extend ethtool statistics (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: misc fixes (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Fix port reset (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add ethtool support (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add MDIO support (Iyappan Subramanian) [1383485]
- [netdrv] maintainers: Add entry for APM X-Gene SoC Ethernet (v2) driver (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add transmit and receive (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add base driver (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add ethernet hardware configuration (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add mac configuration (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add DMA descriptor (Iyappan Subramanian) [1383485]
- [redhat] kconfig: Enable XIVE and XIVE_NATIVE for Power 9 (Steve Best) [1320898]
- [powerpc] 64s: Revert setting of LPCR(LPES) on POWER9 (Steve Best) [1320898]
- [powerpc] powernv: Add XIVE related definitions to opal-api.h (Steve Best) [1320898]
- [powerpc] Fixup LPCR:PECE and HEIC setting on POWER9 (Steve Best) [1320898]
- [powerpc] Consolidate variants of real-mode MMIOs (Steve Best) [1320898]
- [powerpc] kvm: Remove obsolete kvm_vm_ioctl_xics_irq declaration (Steve Best) [1320898]
- [powerpc] kvm: Make kvmppc_xics_create_icp static (Steve Best) [1320898]
- [powerpc] kvm: Massage order of #include (Steve Best) [1320898]
- [powerpc] xive: Native exploitation of the XIVE interrupt controller (Steve Best) [1320898]
- [powerpc] smp: Remove migrate_irq() custom implementation (Steve Best) [1320898]
- [powerpc] Add optional smp_ops->prepare_cpu SMP callback (Steve Best) [1320898]
- [powerpc] Add more PPC bit conversion macros (Steve Best) [1320898]
- [redhat] aarch64: configs: Enable DesignWare GPIO (Iyappan Subramanian) [1429651]
- [gpio] dwapb: Add support for next generation of X-Gene SoC (Iyappan Subramanian) [1429651]
- [arm64] DO NOT UPSTREAM - Enable workaround for accessing ICC_SRE_EL2 (Wei Huang) [1442825]
- [arm64] qcom: Add defines for ARMv8 implementer (MIDR) (Wei Huang) [1442825]
- [acpi] iort: Fix CONFIG_IOMMU_API dependency (Jun Ma) [1266462]
- [acpi] iort: Remove linker section for IORT entries probing (Jun Ma) [1266462]
- [iommu] arm-smmu: Clean up early-probing workarounds (Jun Ma) [1266462]
- [arm64] dma-mapping: Remove the notifier trick to handle early setting of dma_ops (Jun Ma) [1266462]
- [acpi] drivers: acpi: Handle IOMMU lookup failure with deferred probing or error (Jun Ma) [1266462]
- [iommu] of: Handle IOMMU lookup failure with deferred probing or error (Jun Ma) [1266462]
- [of] acpi: Configure dma operations at probe time for platform/amba/pci bus devices (Jun Ma) [1266462]
- [of] device: Fix overflow of coherent_dma_mask (Jun Ma) [1266462]
- [acpi] iort: Add function to check SMMUs drivers presence (Jun Ma) [1266462]
- [of] dma: Make of_dma_deconfigure() public (Jun Ma) [1266462]
- [iommu] of: Prepare for deferred IOMMU configuration (Jun Ma) [1266462]
- [iommu] of: Refactor of_iommu_configure() for error handling (Jun Ma) [1266462]
- [misc] cxl: Add psl9 specific code (Steve Best) [1320907]
- [misc] cxl: Isolate few psl8 specific calls (Steve Best) [1320907]
- [misc] cxl: Rename some psl8 specific functions (Steve Best) [1320907]
- [misc] cxl: Update implementation service layer (Steve Best) [1320907]
- [misc] cxl: Keep track of mm struct associated with a context (Steve Best) [1320907]
- [misc] cxl: Remove unused values in bare-metal environment (Steve Best) [1320907]
- [misc] cxl: Read vsec perst load image (Steve Best) [1320907]
- [arm64] vdso: Remove ISB from gettimeofday (Robert Richter) [1445440]
- [arm64] vdso: Rewrite gettimeofday into C (Robert Richter) [1445440]
- [redhat] configs: enable CONFIG_NF_SOCKET_IPV4 and CONFIG_NF_SOCKET_IPV6 (Davide Caratti) [1436771]
- [redhat] config: enable CHECKPOINT_RESTORE only on x86_64 and powerpc64 (Aristeu Rozanski) [1391536]
- Revert "[redhat] aarch64: configs: Enable Qlogic networking support" ("Herton R. Krzesinski")

* Tue May 09 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-2.el7]
- [ethernet] bnx2x: Align RX buffers (Scott Wood) [1438582]
- [acpi] Continue to ignore interrupt producer/consumer flag (Jeremy Linton) [1448077]
- [i2c] thunderx: Enable HWMON class probing (Robert Richter) [1448181]
- [acpi] apd: Add clock frequency for Hisilicon Hip07/08 I2C controller (Jun Ma) [1403804]
- [i2c] designware: Add ACPI HID for Hisilicon Hip07/08 I2C controller (Jun Ma) [1403804]
- [redhat] aarch64:configs: Enable desingware I2C controller (Jun Ma) [1403804]
- [redhat] aarch64: configs: Enable Qlogic networking support (Zhou Wang) [1266393]
- [redhat] aarch64: configs: Enable HiSilicon VGA (Zhou Wang) [1266321]
- [fs] iomap_dio_rw: Prevent reading file data beyond iomap_dio->i_size (Gustavo Duarte) [1444708]
- [acpi] arm64: Add SBSA Generic Watchdog support in GTDT driver (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: add GTDT support for memory-mapped timer (Jun Ma) [1403765]
- [acpi] arm64: Add memory-mapped timer support in GTDT driver (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: simplify ACPI support code (Jun Ma) [1403765]
- [acpi] arm64: Add GTDT table parse driver (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: split MMIO timer probing (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: add structs to describe MMIO timer (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: move arch_timer_needs_of_probing into DT init call (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: refactor arch_timer_needs_probing (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: split dt-only rate handling (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: rework PPI selection (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: add a new enum for spi type (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: move enums and defines to header file (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: rename the PPI enum (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: rename type macros (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: clean up printk usage (Jun Ma) [1403765]
- [arm64] arch_timer: Add HISILICON_ERRATUM_161010101 ACPI matching data (Jun Ma) [1439440]
- [arm64] arch_timer: Allow erratum matching with ACPI OEM information (Jun Ma) [1439440]
- [arm64] arch_timer: Workaround for Cortex-A73 erratum 858921 (Jun Ma) [1439440]
- [arm64] arch_timer: Enable CNTVCT_EL0 trap if workaround is enabled (Jun Ma) [1439440]
- [arm64] arch_timer: Save cntkctl_el1 as a per-cpu variable (Jun Ma) [1439440]
- [arm64] arch_timer: Move clocksource_counter and co around (Jun Ma) [1439440]
- [arm64] arch_timer: Allows a CPU-specific erratum to only affect a subset of CPUs (Jun Ma) [1439440]
- [arm64] arch_timer: Make workaround methods optional (Jun Ma) [1439440]
- [arm64] arch_timer: Rework the set_next_event workarounds (Jun Ma) [1439440]
- [arm64] arch_timer: Get rid of erratum_workaround_set_sne (Jun Ma) [1439440]
- [arm64] arch_timer: Move arch_timer_reg_read/write around (Jun Ma) [1439440]
- [arm64] arch_timer: Add erratum handler for CPU-specific capability (Jun Ma) [1439440]
- [arm64] arch_timer: Add infrastructure for multiple erratum detection methods (Jun Ma) [1439440]
- [arm64] cpu_errata: Add capability to advertise Cortex-A73 erratum 858921 (Jun Ma) [1439440]
- [arm64] cpu_errata: Allow an erratum to be match for all revisions of a core (Jun Ma) [1439440]
- [arm64] Define Cortex-A73 MIDR (Jun Ma) [1439440]
- [arm64] Add CNTVCT_EL0 trap handler (Jun Ma) [1439440]
- [arm64] Allow checking of a CPU-local erratum (Jun Ma) [1439440]
- [irqchip] gic-v3-its: Add IORT hook for platform MSI support (Jun Ma) [1266314]
- [irqchip] mbigen: Add ACPI support (Jun Ma) [1266314]
- [irqchip] mbigen: Introduce mbigen_of_create_domain() (Jun Ma) [1266314]
- [irqchip] mbigen: Drop module owner (Jun Ma) [1266314]
- [base] platform-msi: Make platform_msi_create_device_domain() ACPI aware (Jun Ma) [1266314]
- [acpi] platform: setup MSI domain for ACPI based platform device (Jun Ma) [1266314]
- [acpi] platform-msi: retrieve devid from IORT (Jun Ma) [1266314]
- [acpi] iort: Introduce iort_node_map_platform_id() to retrieve dev id (Jun Ma) [1266314]
- [acpi] iort: Rename iort_node_map_rid() to make it generic (Jun Ma) [1266314]
- [irqchip] gicv3-its: platform-msi: Scan MADT to create platform msi domain (Jun Ma) [1266314]
- [irqchip] gicv3-its: platform-msi: Refactor its_pmsi_init() to prepare for ACPI (Jun Ma) [1266314]
- [irqchip] gicv3-its: platform-msi: Refactor its_pmsi_prepare() (Jun Ma) [1266314]
- [irqchip] gic-v3-its: Keep the include header files in alphabetic order (Jun Ma) [1266314]
- [acpi] iort: Rework iort_match_node_callback() return value handling (Jun Ma) [1266314]
- [acpi] iort: Add missing comment for iort_dev_find_its_id() (Jun Ma) [1266314]
- [acpi] iort: Fix the indentation in iort_scan_node() (Jun Ma) [1266314]
- [redhat] Modify CONFIG_UPROBE_EVENT and CONFIG_KPROBE_EVENT (Pratyush Anand) [1448376]

* Wed May 03 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-1.el7]
- [acpi] pci: Add MCFG quirk for 2nd node of Cavium ThunderX pass2.x host controller (Robert Richter) [1430388]
- [redhat] copy blk-wbt.h and blk-stat.h headers in kernel-devel package ("Herton R. Krzesinski") [1440236]
- [ata] ahci: thunderx2: Fix for errata that affects stop engine (Robert Richter) [1430391]
- [redhat] aarch64: configs: Enable ARCH_THUNDER2 (Robert Richter) [1414532]
- [gpio] xlp: Update for ARCH_THUNDER2 (Robert Richter) [1414532]
- [spi] xlp: update for ARCH_VULCAN2 (Robert Richter) [1414532]
- [iommu] arm-smmu, acpi: Enable Cavium SMMU-v2 (Robert Richter) [1427523]
- [iommu] arm-smmu: Print message when Cavium erratum 27704 was detected (Robert Richter) [1427523]
- [iommu] arm-smmu: Fix 16bit ASID configuration (Robert Richter) [1427523]
- [redhat] aarch64: configs: Enable edac support for Cavium CN88xx (Robert Richter) [1243040]
- [edac] thunderx: Add Cavium ThunderX EDAC driver (Robert Richter) [1243040]
- [redhat] aarch64: Enable CONFIG_CRASH_DUMP (Pratyush Anand) [1388289]
- [char] ipmi_si: use smi_num for init_name (Tony Camuso) [1435727]
- [i2c] thunderx: ACPI support for clock settings (Robert Richter) [1268499]
- [i2c] xlp9xx: update for ARCH_THUNDER2 (Robert Richter) [1268499]
- [arm64] redhat: crashkernel auto reservation code for ARM64 (Pratyush Anand) [1388289 1342670 1390457]
- [firmware] efi/libstub/arm*: Set default address and size cells values for an empty dtb (Pratyush Anand) [1388289 1342670 1390457]
- [documentation] dt: chosen properties for arm64 kdump (Pratyush Anand) [1388289 1342670 1390457]
- [documentation] kdump: describe arm64 port (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] kdump: enable kdump in defconfig (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] kdump: provide /proc/vmcore file (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] kdump: add VMCOREINFO's for user-space tools (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] kdump: implement machine_crash_shutdown() (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] hibernate: preserve kdump image around hibernation (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] kdump: protect crash dump kernel memory (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] mm: add set_memory_valid() (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] kdump: reserve memory for crash dump kernel (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] limit memory regions based on DT property, usable-memory-range (Pratyush Anand) [1388289 1342670 1390457]
- [mm] memblock: add memblock_cap_memory_range() (Pratyush Anand) [1388289 1342670 1390457]
- [mm] memblock: add memblock_clear_nomap() (Pratyush Anand) [1388289 1342670 1390457]
- [redhat] aarch64: configs: Enable crypto support for Cavium CN88xx (Robert Richter) [1404503]
- [redhat] configs: Enable CRYPTO_CRC32C_ARM64 (Herbert Xu) [1370247]
- [base] cacheinfo: let arm64 provide cache info without using DT or ACPI (Al Stone) [1382130 1340200]
- [tty] Fix ldisc crash on reopened tty (Steve Best) [1434165]
- [redhat] docs: require machine parseable upstream commit ids (Jiri Benc)
- [redhat] configs: Enable CONFIG_X86_AMD_PLATFORM_DEVICE (Scott Wood) [1430011]
- [redhat] kconfig: Disable Software IOTLB support for powerpc (Steve Best) [1428506]
- [pci] vulcan: AHCI PCI bar fix for Broadcom Vulcan early silicon (Robert Richter) [1430377]
- [arm64] topology: Adjust sysfs topology (Jonathan Toppins) [1392076]
- [redhat] configs: ppc64: Remove unselectable symbols for unsupported hardware (Scott Wood) [1420897]
- [pci] Workaround for Broadcom Vulcan DMA alias calculation (Robert Richter) [1430372]
- [redhat] aarch64: configs: CN99xx: Add support for Vulcan i2c controller (Robert Richter) [1344226]
- [redhat] kconfig: remove obsolete symbols for ARM64 (Mark Langsdorf) [1425525]
- [redhat] configs: CONFIG_NF_CT_PROTO_* options should be y not m (Prarit Bhargava) [1430505]
- [x86] kdump: crashkernel=X try to reserve below 896M first, then try below 4G, then MAXMEM (Xunlei Pang) [1375960]
- [powerpc] kdump: Adjust crashkernel reservation for 2GB-4GB systems (Xunlei Pang) [1375960]
- [powerpc] kdump: Support crashkernel auto memory reservation on a system with 2GB or more (Xunlei Pang) [1375960]
- [powerpc] kdump: Set crashkernel 'auto' memory reservation threshold to 2GB (Xunlei Pang) [1375960]
- [s390x] kdump: Increase crashkernel=auto base reservation from 128M to 160M (Xunlei Pang) [1375960]
- [kernel] kdump: Increase x86 crashkernel=auto base reservation from 128M to 160M (Xunlei Pang) [1375960]
- [kernel] kdump: Improve logging when crashkernel=auto can't be satisfied (Xunlei Pang) [1375960]
- [s390x] kdump: Use 4 GiB for KEXEC_AUTO_THRESHOLD (Xunlei Pang) [1375960]
- [kdump] crashkernel=auto fixes and cleanup (Xunlei Pang) [1375960]
- [kdump] Add crashkernel=auto support (Xunlei Pang) [1375960]
- [fs] revert "libxfs: pack the agfl header structure so XFS_AGFL_SIZE is correct" (Eric Sandeen) [1411637]
- [redhat] kconfig: Disable HIBERNATION for powerpc (Steve Best) [1422587]
- [redhat] aarch64: configs: Disable X-Gene PktDMA driver (Jeffrey Bastian) [1408300]
- [redhat] aarch64: configs: Enable Cavium HW RNG module (David Daney) [1385929]
- [redhat] configs: enable CONFIG_VFIO_NOIOMMU for aarch64 (William Townsend) [1418087]
- [redhat] configs: disable CONFIG_SERIAL_8250 on s390x ("Herton R. Krzesinski") [1418787]
- [redhat] enable s390x build again for testing ("Herton R. Krzesinski") [1410579]
- [s390x] add zfcpdump user space tools from RHEL 7 ("Herton R. Krzesinski") [1410579]
- [redhat] rhmaintainers: update files list and maintainer for infiniband (Jonathan Toppins)
- [redhat] rhmaintainers: update tg3 and bna maintainer fields with jtoppins (Jonathan Toppins)
- [redhat] rhmaintainers: update bnxt_en maintainer info (Jonathan Toppins)
- [redhat] aarch64: configs: enable _en bits of mlx5 driver (Jonathan Toppins) [1404081]
- [redhat] add support for aarch64 in rh-cross-* make targets (Al Stone) [1415855]
- [redhat] build-configs.sh: simplify config building (Jonathan Toppins)
- [makefile] arm64, powerpc, x86: Add -Werror to kernel build ("Herton R. Krzesinski") [1404449]
- [makefile] Revert "Fix gcc-4.9.0 miscompilation of load_balance() in scheduler" ("Herton R. Krzesinski") [1387899]
- [redhat] rhmaintainers: add Amazon Ethernet Drivers entry (Vitaly Kuznetsov)
- [redhat] configs: enable LIO iSCSI target mode for cxgb4 (Jonathan Toppins) [1405565]
- [redhat] configs: Enable IMA and INTEGRITY by default ("Herton R. Krzesinski") [1326888]
- [tty] 8250_dw: quirk lack of spcr driver's ability to report mmio32 (Jonathan Toppins) [1406924]
- [char] crash: add crash driver (Dave Anderson) [1398016]
- [arm64] acpi: prefer booting with ACPI over DTS (Jonathan Toppins) [1405174]
- [redhat] config: re-enable RDMAVT and HFI1 due to defaults change (Jonathan Toppins) [1409890]
- [redhat] add missing .gitattributes directives from RHEL 7 setup ("Herton R. Krzesinski")
- [redhat] configs: enable Amazon Elastic Network Adapter ("Herton R. Krzesinski")
- [redhat] configs: enable CONFIG_CRYPTO_DEV_CHELSIO=m ("Herton R. Krzesinski")
- [redhat] RHMAINTAINERS: update Kernel Maintainer entry ("Herton R. Krzesinski")
- [redhat] genspec.sh: do not hide arm64 changelog entries ("Herton R. Krzesinski")
- [redhat] configs: disable CONFIG_USELIB on all architectures ("Herton R. Krzesinski") [1388940]
- [redhat] configs: enable driver for X-Gene hardware sensors (Jeffrey Bastian) [1400331]
- [arch] arm64: Workaround for QDF2432 ID_AA64 SR accesses (Mark Langsdorf) [1389083]
- [kernel] kbuild: AFTER_LINK (Roland McGrath)
- [redhat] scripts/new_release.sh: do not increment PREBUILD line ("Herton R. Krzesinski")
- [redhat] determine proper tag on initial release ("Herton R. Krzesinski")
- [redhat] rh-dist-git: fix update of dist-git sources file for linux tarball ("Herton R. Krzesinski")
- [redhat] scripts/rh-dist-git.sh: fix the upload of the kabi tarball ("Herton R. Krzesinski")
- [redhat] update git/files and .gitignore after latest kabi changes ("Herton R. Krzesinski")
- [redhat] kabi: enable kernel-abi-whitelists package and kabi-check (Petr Oros)
- [redhat] kabi: show-kabi: allow empty whitelist (Petr Oros)
- [redhat] kabi: add support for aarch64 (Petr Oros)
- [redhat] kabi: remove support for s390x (Petr Oros)
- [redhat] kabi: remove support for ppc64 (Petr Oros)
- [redhat] kabi: clean all symbols in x86_64 (Petr Oros)
- [redhat] kabi: clean all symbols in ppc64le (Petr Oros)
- [redhat] Remove dup scripts from kernel tree (Petr Oros)
- [redhat] configs: set to y accelerated implementations of CONFIG_CRYPTO_AES ("Herton R. Krzesinski") [1397913]
- [redhat] configs: set CONFIG_CRYPTO_DRBG_MENU=y ("Herton R. Krzesinski") [1397913]
- [redhat] spec: include missing arch/arm/include into devel package (Petr Oros) [1397407]
- [redhat] make sure we create changelogs and look at tags with right package name ("Herton R. Krzesinski")
- [redhat] rh-dist-git.sh: give the package name to clone_tree.sh ("Herton R. Krzesinski")
- [redhat] configs: add missing changes to lib/ configuration (Aristeu Rozanski)
- [init] enable CHECKPOINT_RESTORE (Aristeu Rozanski) [1391536]
- [redhat] Makefiles: remove extra inclusions (Jonathan Toppins)
- [redhat] allow building binaries with different name from src.rpm ("Herton R. Krzesinski")
- [redhat] config review: enable NVME_TARGET_LOOP/NVME_TARGET_RDMA ("Herton R. Krzesinski")
- [redhat] config review: remove/disable deprecated scsi/storage drivers ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_SCSI_SNIC=n ("Herton R. Krzesinski")
- [redhat] config review: delete removed drivers/scsi options ("Herton R. Krzesinski")
- [redhat] configs: merge requested changes for watchdog support (Aristeu Rozanski)
- [redhat] configs: merge changes for RTC (Aristeu Rozanski)
- [redhat] config review: make sure we disable drivers for some obsolete scsi hw ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_SCSI_AIC7XXX_OLD ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_REGULATOR related options ("Herton R. Krzesinski")
- [redhat] configs: merge comments on USB (Aristeu Rozanski)
- [redhat] config review: do not disable CEPH_FS on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: fix/cleanup CONFIG_PWM_LPSS* configs ("Herton R. Krzesinski")
- [redhat] config review: BATTERY_BQ27x00 renamed to BATTERY_BQ27XXX ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_DELL_SMBIOS=m on x86_64 ("Herton R. Krzesinski")
- [redhat] config review: move existing x86 platform options to x86_64 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_MTD_BLKDEVS ("Herton R. Krzesinski")
- [redhat] config review: mark some CONFIG_MTD_* options as disabled ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_MTD_NAND_* options ("Herton R. Krzesinski")
- [redhat] configs: merge changes for PCI (Aristeu Rozanski)
- [redhat] config review: delete CONFIG_MMC_SDRICOH_CS ("Herton R. Krzesinski")
- [redhat] configs: merge comments for NVMEM, NVME, OF, NTB (Aristeu Rozanski)
- [redhat] config review: cleanup CONFIG*INTEL_MID* options ("Herton R. Krzesinski")
- [redhat] config review: delete INTEL_MEI/VMWARE_BALLOON from generic ("Herton R. Krzesinski")
- [redhat] config review: cleanup auto selected options from drivers/misc ("Herton R. Krzesinski")
- [redhat] config review: delete hidden drivers/misc options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_SENSORS_BH1780 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_ATMEL_PWM ("Herton R. Krzesinski")
- [redhat] config review: mark all new CONFIG_MFD_* options as disabled ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_MEMSTICK_REALTEK_USB=m on x86_64 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_DM_CACHE_MQ ("Herton R. Krzesinski")
- [redhat] config review: cleanup BCACHE options ("Herton R. Krzesinski")
- [redhat] config review: disable DM_LOG_WRITES/DM_VERITY_FEC ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_XGENE_SLIMPRO_MBOX=m on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_NVM=n ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_LEDS_TRIGGER_PANIC=n ("Herton R. Krzesinski")
- [redhat] config review: LEDS_TRIGGER_IDE_DISK renamed to LEDS_TRIGGER_DISK ("Herton R. Krzesinski")
- [redhat] config review: LEDS_PCA9633 renamed to LEDS_PCA963X ("Herton R. Krzesinski")
- [redhat] config review: ISDN_DRV_AVMB1_VERBOSE_REASON renamed ("Herton R. Krzesinski")
- [redhat] configs: set HZ to 100 across all arches ("Herton R. Krzesinski")
- [redhat] configs: adjust HID options based on feedback (Aristeu Rozanski)
- [redhat] config review: delete CONFIG_AMD_IOMMU_STATS ("Herton R. Krzesinski")
- [redhat] config review: disable CONFIG_IIO on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_I2C_INTEL_MID ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_SENSORS_I5500=m on x86_64 ("Herton R. Krzesinski")
- [redhat] configs: adjust input config options for arm64 (Aristeu Rozanski)
- [redhat] config review: change/cleanup some drivers/gpu options on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: initial review of drivers/gpu options ("Herton R. Krzesinski")
- [redhat] config review: cleanup some GPIO options ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_FW_CFG_SYSFS=n ("Herton R. Krzesinski")
- [redhat] config review: disable CONFIG_DEV_DAX ("Herton R. Krzesinski")
- [redhat] config review: merge feedback from CONFIG_TCG_* ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_STALDRV ("Herton R. Krzesinski")
- [redhat] configs: update drivers/media config options (Aristeu Rozanski)
- [redhat] config review: cleanup most of options which depends on PCMCIA ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_CRASH settings ("Herton R. Krzesinski")
- [redhat] config review: review CONFIG_DEVMEM and its related settings ("Herton R. Krzesinski")
- [redhat] config review: ARM_CCI500_PMU renamed to ARM_CCI5xx_PMU ("Herton R. Krzesinski")
- [redhat] config review: disable bluetooth on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_PARIDE_* options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_DRBD_FAULT_INJECTION ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_CISS_SCSI_TAPE ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_XEN_BLKDEV_BACKEND ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_BLK_DEV_HD* ("Herton R. Krzesinski")
- [redhat] config review: fix value of CONFIG_BLK_DEV_SKD ("Herton R. Krzesinski")
- [redhat] config review: keep CONFIG_BLK_DEV_SKD disabled ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_BLK_CPQ_DA ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_BCMA_BLOCKIO ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_ATM_* options related to drivers ("Herton R. Krzesinski")
- [redhat] configs: disable all sound modules on arm64 (Aristeu Rozanski)
- [redhat] config review: delete CONFIG_A11Y_BRAILLE_CONSOLE ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_UEVENT_HELPER* ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_FW_LOADER_USER_HELPER* ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_KVM_MMIO ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_XEN_NETDEV_BACKEND ("Herton R. Krzesinski")
- [redhat] config review: WL_TI was renamed to WLAN_VENDOR_TI ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_ZYDAS=n ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_ST=n ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_RSI=n ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_CISCO=n ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_ATMEL=n ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_ADMTEK=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup options which depends on NET_VENDOR_WIZNET ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_WL12XX_* options ("Herton R. Krzesinski")
- [redhat] config review: cleanup options related to NET_VENDOR_VIA ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_USB_CDC_PHONET ("Herton R. Krzesinski")
- [redhat] config review: cleanup options which depends on NET_VENDOR_3COM ("Herton R. Krzesinski")
- [redhat] config review: drop CONFIG_TEHUTI ("Herton R. Krzesinski")
- [redhat] config review: cleanup options which depends on NET_VENDOR_STMICRO ("Herton R. Krzesinski")
- [redhat] config review: don't disable SLIP on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup options which depends on FDDI ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_SIS* options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_SC92031 ("Herton R. Krzesinski")
- [redhat] config review: cleanup options related to NET_VENDOR_EXAR ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_RTL8XXXU=m ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_R6040 ("Herton R. Krzesinski")
- [redhat] config review: delete QEDE_GENEVE/QEDE_VXLAN ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_INTERSIL=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup some CONFIG_PCMCIA_* options (network drivers) ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_PCH_GBE ("Herton R. Krzesinski")
- [redhat] config review: cleanup P54 related options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_NET_VENDOR_XIRCOM ("Herton R. Krzesinski")
- [redhat] adjust tty config options (Aristeu Rozanski)
- [redhat] config review: set NET_VENDOR_SAMSUNG/NET_VENDOR_SYNOPSYS=n ("Herton R. Krzesinski")
- [redhat] config review: enable ROCKER ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_NET_VENDOR_RENESAS=n ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_NET_VENDOR_QUALCOMM=y for aarch64 ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_NET_VENDOR_QUALCOMM=n for everyone ("Herton R. Krzesinski")
- [redhat] config review: cleanup NET_VENDOR_FARADAY/NET_VENDOR_FUJITSU ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_NET_VENDOR_EZCHIP=n for everyone ("Herton R. Krzesinski")
- [redhat] config review: disable CONFIG_NET_VENDOR_CAVIUM on ppc64le/x86_64 ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_NET_VENDOR_AGERE=n for everyone ("Herton R. Krzesinski")
- [redhat] config review: remove NET_VENDOR_8390 and options that depends on it ("Herton R. Krzesinski")
- [redhat] config review: cleanup options related to NET_VENDOR_NATSEMI ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_NET_CALXEDA_XGMAC ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_MT7601U=m ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_MLXSW_CORE=m on aarch64 and x86_64 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_MLX4_EN_VXLAN ("Herton R. Krzesinski")
- [redhat] config review: cleanup remaining HAMRADIO driver related options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_THUNDER_NIC_BGX ("Herton R. Krzesinski")
- [redhat] config review: do not disable MACSEC on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup LIBERTAS options ("Herton R. Krzesinski")
- [redhat] config review: cleanup options related to NET_VENDOR_MICREL ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_IWLWIFI* options ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_IPW* options ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_IPVLAN=n ("Herton R. Krzesinski")
- [redhat] config review: config changes for removed IP1000 option ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_I40E_VXLAN ("Herton R. Krzesinski")
- [redhat] config review: cleanup options which depends on HERMES ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_FORCEDETH ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_FM10K_VXLAN ("Herton R. Krzesinski")
- [redhat] config review: move CONFIG_NET_VENDOR_MICROCHIP to generic ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_EMAC_ROCKCHIP ("Herton R. Krzesinski")
- [redhat] config review: cleanup options which depend on IRDA ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_DMASCC ("Herton R. Krzesinski")
- [redhat] config review: cleanup NET_VENDOR_DLINK related options ("Herton R. Krzesinski")
- [redhat] config review: cleanup ATALK related options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_CHELSIO_T1_1G ("Herton R. Krzesinski")
- [redhat] config review: cleanup options under NET_VENDOR_SUN ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_CAN_SJA1000_OF_PLATFORM ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_CAN_M_CAN=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_BRCM* options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_BPQETHER ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_BE2NET_VXLAN ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_BCM63XX_PHY ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_BAYCOM_* options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_B44_PCI ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_B43LEGACY_* options ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_B43_* options ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_ATH9K options ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_ATH6KL* settings ("Herton R. Krzesinski")
- [redhat] config review: cleanup ATH5K settings ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_ALI_FIR ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_ADAPTEC_STARFIRE ("Herton R. Krzesinski")
- [redhat] config review: cleanup ACT200L/ACTISYS_DONGLE ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_ACENIC* settings ("Herton R. Krzesinski")
- [redhat] config review: more misc cleanup on some init/ options (Aristeu Rozanski)
- [redhat] config review: delete CONFIG_6PACK ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_ARM_AT91_ETHER ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_TRACE_BRANCH_PROFILING ("Herton R. Krzesinski")
- [redhat] config review: TRACEPOINT_BENCHMARK/TRACE_ENUM_MAP_FILE/TRACING_EVENTS_GPIO ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_PREEMPT_TRACER ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_PM_* options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_PM_OPP ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_VIRT_CPU_ACCOUNTING ("Herton R. Krzesinski")
- [redhat] config review: do not disable NO_HZ_FULL on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_LIVEPATCH ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_INTEGRITY_AUDIT=y ("Herton R. Krzesinski")
- [redhat] config review: mark some IMA options as disabled ("Herton R. Krzesinski")
- [redhat] config review: cleanup/move IMA options ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_EVM_LOAD_X509=n ("Herton R. Krzesinski")
- [redhat] config review: replace EVM_HMAC_VERSION with EVM_ATTR_FSUUID ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_GENERIC_CLOCKEVENTS_BUILD ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_CLOCKSOURCE_WATCHDOG ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_RD_LZ4=y ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_KEYS_DEBUG_PROC_KEYS ("Herton R. Krzesinski")
- [redhat] config review: set n to KEY_DH_OPERATIONS/SECURITY_LOADPIN ("Herton R. Krzesinski")
- [redhat] config review: do not disable CRYPTO_TEST on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup/delete PKCS7_MESSAGE_PARSER files ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_CRYPTO_ZLIB ("Herton R. Krzesinski")
- [redhat] config review: enable requested CRYPTO_SHA* options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_CRYPTO_SALSA20_586 ("Herton R. Krzesinski")
- [redhat] config review: cleanup/check CRYPTO_POLY1305* settings ("Herton R. Krzesinski")
- [redhat] config review: delete CRYPTO_LZO/CRYPTO_MD5 ("Herton R. Krzesinski")
- [redhat] config review: remove/disable CRYPTO_LZ4/CRYPTO_LZ4HC ("Herton R. Krzesinski")
- [redhat] config review: remove CONFIG_CRYPTO_KEYWRAP from aarch64 ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_CRYPTO_CTR=m ("Herton R. Krzesinski")
- [redhat] config review: ensure we set newer *CRYPTO_USER_API* ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_CRYPTO_DES3_EDE_X86_64=m ("Herton R. Krzesinski")
- [redhat] config review: enable chacha20 on other arches ("Herton R. Krzesinski")
- [redhat] config review: cleanup CRYPTO_MCRYPTD specific setting ("Herton R. Krzesinski")
- [redhat] config review: move CRYPTO_CRC32C_INTEL under x86_64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup some unselectable crypto options ("Herton R. Krzesinski")
- [redhat] config review: move some CONFIG_X86_* options under x86_64 ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_X86_INTEL_MEMORY_PROTECTION_KEYS=y ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_X86_DEBUG_FPU only on -debug ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_RANDOMIZE_BASE=n ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_TUNE_CELL ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_PPC_RADIX_MMU=y for ppc64le ("Herton R. Krzesinski")
- [redhat] config review: more misc cleanup on some arch options ("Herton R. Krzesinski")
- [redhat] config review: enable/set CONFIG_PERF_EVENTS_* options ("Herton R. Krzesinski")
- [redhat] config review: misc cleanup on some arch options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_NO_BOOTMEM ("Herton R. Krzesinski")
- [redhat] config review: cleanup/delete CONFIG_HAVE_* options ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_GCC_PLUGINS=n ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_GEN_RTC_X ("Herton R. Krzesinski")
- [redhat] configs: enable CONFIG_SECTION_MISMATCH_WARN_ONLY for now (Aristeu Rozanski)
- [redhat] config review: delete CONFIG_DIRECT_GBPAGES ("Herton R. Krzesinski")
- [redhat] config review: move some x86_64 CONFIG_DEBUG* options ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_DEBUG_WX=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup and fix DEBUG_RODATA* settings ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_DEBUG_ENTRY=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup/fix stack protector settings ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_ARM64_VA_BITS_48=y ("Herton R. Krzesinski")
- [redhat] config review: update ARCH_EXYNOS setting ("Herton R. Krzesinski")
- [redhat] config review: delete MFD_TIMBERDALE/TIMB_DMA settings ("Herton R. Krzesinski")
- [redhat] config review: enable QCOM_HIDMA* on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_PCH_DMA ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_INTEL_MID_DMAC ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_NET_DMA_RH_KABI ("Herton R. Krzesinski")
- [redhat] config review: update for IDMA64 config rename ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_DW_DMAC_BIG_ENDIAN_IO ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_EDAC_SKX=m on x86_64 ("Herton R. Krzesinski")
- [redhat] config review: merge lib related options (Aristeu Rozanski)
- [redhat] config review: adjust for mce_amd_inj config option rename ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_ARM_CPUIDLE on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_CPU_IDLE_MULTIPLE_DRIVERS ("Herton R. Krzesinski")
- [redhat] config review: IB driver changes on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: delete IB options which are gone ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_RDMA_RXE=m ("Herton R. Krzesinski")
- [redhat] config review: don't disable Infiniband on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_TIPC_MEDIA_IB ("Herton R. Krzesinski")
- [redhat] config review: merge CONFIG_TCP_CONG* settings ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_ROSE ("Herton R. Krzesinski")
- [redhat] config review: cleanup for remaining RFKILL options ("Herton R. Krzesinski")
- [redhat] config review: keep RFKILL_GPIO enabled only on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup any remaining CONFIG_RDS_* ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_*NETDEV options ("Herton R. Krzesinski")
- [redhat] config review: set NF_LOG_ARP and NF_LOG_BRIDGE for everyone ("Herton R. Krzesinski")
- [redhat] config review: don't disable NF_CT_NETLINK_TIMEOUT on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: don't disable NF_CONNTRACK_TIMEOUT on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: update NF_CONNTRACK_IPV4/6 ("Herton R. Krzesinski")
- [redhat] config review: enable NET_SWITCHDEV on all arches ("Herton R. Krzesinski")
- [redhat] config review: merge CONFIG_NET_SCH* settings ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_NETROM ("Herton R. Krzesinski")
- [redhat] config review: fix renamed NETPRIO cgroup setting ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_NET_NCSI=n ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_NETLINK_MMAP setting ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_NET_L3_MASTER_DEV=n ("Herton R. Krzesinski")
- [redhat] config review: merge CONFIG_NETFILTER* settings ("Herton R. Krzesinski")
- [redhat] config review: merge CONFIG_NET_* options ("Herton R. Krzesinski")
- [redhat] config review: cleanup NET_9P settings ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_MPLS_ROUTING=n ("Herton R. Krzesinski")
- [redhat] config review: do not unset NET_DEVLINK on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup some unselectable net options ("Herton R. Krzesinski")
- [redhat] config review: always enable IP_VS_FO/IP_VS_OVF ("Herton R. Krzesinski")
- [redhat] config review: don't disable IPV6_GRE on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_IPV6_ILA=n ("Herton R. Krzesinski")
- [redhat] config review: disable net *FOU* options ("Herton R. Krzesinski")
- [redhat] config review: merge config feedback on missing ipset modules ("Herton R. Krzesinski")
- [redhat] config review: fix CONFIG_IP_NF_TARGET_REJECT setting ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_IP_NF_TARGET_ULOG ("Herton R. Krzesinski")
- [redhat] config review: fix IP_NF_FILTER setting ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_INET_LRO ("Herton R. Krzesinski")
- [redhat] config review: disable CONFIG_HSR/CONFIG_INET_DIAG_DESTROY ("Herton R. Krzesinski")
- [redhat] config review: always disable CONFIG_CGROUP_NET_PRIO ("Herton R. Krzesinski")
- [redhat] config review: fix CONFIG_BRIDGE_NETFILTER=m ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_BRIDGE_EBT_ULOG ("Herton R. Krzesinski")
- [redhat] config review: cleanup and enable BPF_JIT also on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup/remove AX25 options ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_AF_KCM=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup fs related options ("Herton R. Krzesinski")
- [redhat] config review: don't disable FS_DAX on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: disable GFS2 and DLM ("Herton R. Krzesinski")
- [redhat] config review: disable btrfs ("Herton R. Krzesinski")
- [redhat] config review: don't disable QUOTA_DEBUG on aarch64 -debug ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_PNFS_FILE_LAYOUT=m ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_ORANGEFS_FS=n ("Herton R. Krzesinski")
- [redhat] config review: additional cleanup/changes for NFS settings ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_NFSD_FAULT_INJECTION=y for aarch64 -debug ("Herton R. Krzesinski")
- [redhat] config review: remove specific CONFIG_NFSD_SCSILAYOUT setting on arm ("Herton R. Krzesinski")
- [redhat] config review: mark NFSD_BLOCKLAYOUT/NFSD_FLEXFILELAYOUT as disabled ("Herton R. Krzesinski")
- [redhat] config review: don't make NFS builtin on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_FS_ENCRYPTION=n ("Herton R. Krzesinski")
- [redhat] config review: make CONFIG_FSCACHE_OBJECT_LIST setting consistent ("Herton R. Krzesinski")
- [redhat] config review: update for renamed CONFIG_EXT4_USE_FOR_EXT23 ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_EXT4_ENCRYPTION=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup 9P_FS options ("Herton R. Krzesinski")
- [redhat] config review: cleanup removed acpi options ("Herton R. Krzesinski")
- [redhat] config review: set always CONFIG_ACPI_TABLE_UPGRADE=y ("Herton R. Krzesinski")
- [redhat] config review: review/cleanups of some ACPI configs ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_ACPI_TABLE_UPGRADE on aarch64 non-debug ("Herton R. Krzesinski")
- [redhat] config review: merge acpi debug options ("Herton R. Krzesinski")
- [redhat] config review: disable wlan and wireless on aarch64 and ppc64le ("Herton R. Krzesinski")
- [redhat] config review: disable CONFIG_BPF_SYSCALL ("Herton R. Krzesinski")
- [redhat] config review: don't disable TRANSPARENT_HUGEPAGE on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup SPARSEMEM options ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_ZSMALLOC_STAT ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_Z3FOLD=n ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_IDLE_PAGE_TRACKING on all configs ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_CMA_DEBUGFS=y and CONFIG_DEBUG_PAGE_REF=y for -debug ("Herton R. Krzesinski")
- [redhat] config review: merge remaining ata related options ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_SATA_AHCI_SEATTLE ("Herton R. Krzesinski")
- [redhat] config review: merge block related options ("Herton R. Krzesinski")
- [redhat] Kconfig: Fix CPU_FREQ_STAT setting (Steve Best)
- [redhat] clarify better in the spec why we build headers only for some arches ("Herton R. Krzesinski")
- [redhat] fix architectures being built (Aristeu Rozanski)
- [redhat] get rid of static 'kernel-pegas' and use a central variable (Aristeu Rozanski)
- [redhat] update manually lastcommit (Aristeu Rozanski)
- [redhat] disable hiding of redhat only entries from changelog (Aristeu Rozanski)
- [redhat] change default scratch/official brew build target (Aristeu Rozanski)
- [redhat] disable bootwrapper build if arch is in nobuildarches list ("Herton R. Krzesinski")
- [redhat] disable debug build if arch is in nobuildarches list ("Herton R. Krzesinski")
- [redhat] disable abi whitelists support in the spec file ("Herton R. Krzesinski")
- [redhat] trim/remove old RHEL 7 changelog from the spec file ("Herton R. Krzesinski")
- [redhat] fix make rh-dist-git for kernel-pegas tree ("Herton R. Krzesinski")
- [redhat] rename kernel spec file ("Herton R. Krzesinski")
- [redhat] rename kernel package to kernel-pegas ("Herton R. Krzesinski")
- [redhat] add full support to build aarch64 packages ("Herton R. Krzesinski")
- [redhat] Initial enablement of aarch64 architecture ("Herton R. Krzesinski")
- [redhat] fix-up modules signing (Rafael Aquini)
- [redhat] spec: fix signing_key references (Rafael Aquini)
- [redhat] add missing x509.genkey and extra_certificates files ("Herton R. Krzesinski")
- [redhat] spec: disable arches s390x, ppc64 follow up (Rafael Aquini)
- [redhat] spec: adjust build recipes for the new kernel infrastructure (Rafael Aquini)
- [redhat] disable s390x, s390, i686, ppc64 (Aristeu Rozanski)
- [redhat] move architecture list to Makefile.common (Aristeu Rozanski)
- [redhat] disable kABI check for now (Aristeu Rozanski)
- [redhat] change version to 4.11.0 ("Herton R. Krzesinski")
- [redhat] makefile: make use of proper RHELMAJOR string constant when packaging kabi structures (Rafael Aquini)
- [redhat] configs: match RPMVERSION on generated config files (Rafael Aquini)
- [redhat] import Red Hat specific files (Aristeu Rozanski)


###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
