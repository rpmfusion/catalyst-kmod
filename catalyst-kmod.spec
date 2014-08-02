# buildforkernels macro hint: when you build a new version or a new release
# that contains bugfixes or other improvements then you must disable the
# "buildforkernels newest" macro for just that build; immediately after
# queuing that build enable the macro again for subsequent builds; that way
# a new akmod package will only get build when a new one is actually needed
%global buildforkernels newest

# Tweak to have debuginfo - part 1/2
%if 0%{?fedora} > 7
%define __debug_install_post %{_builddir}/%{?buildsubdir}/find-debuginfo.sh %{_builddir}/%{?buildsubdir}\
%{nil}
%endif

Name:        catalyst-kmod
Version:     14.4
Release:     1%{?dist}.8
# Taken over by kmodtool
Summary:     AMD display driver kernel module
Group:       System Environment/Kernel
License:     Redistributable, no modification permitted
URL:         http://ati.amd.com/support/drivers/linux/linux-radeon.html
Source0:     http://downloads.diffingo.com/rpmfusion/kmod-data/catalyst-kmod-data-%{version}.tar.bz2
Source11:    catalyst-kmodtool-excludekernel-filterfile
Patch0:      compat_alloc-Makefile.patch
Patch1:      3.14_kernel.patch

BuildRoot:   %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# needed for plague to make sure it builds for i686
ExclusiveArch:  i686 x86_64

# get the needed BuildRequires (in parts depending on what we build for)
BuildRequires:  %{_bindir}/kmodtool
%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }
# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} --filterfile %{SOURCE11} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
The catalyst %{version} display driver kernel module.


%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}
# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu} --repo rpmfusion --kmodname %{name} --filterfile %{SOURCE11} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null
%setup -q -c -T -a 0

# Tweak to have debuginfo - part 2/2
%if 0%{?fedora} > 7
cp -p %{_prefix}/lib/rpm/find-debuginfo.sh .
sed -i -e 's|strict=true|strict=false|' find-debuginfo.sh
%endif

mkdir fglrxpkg
%ifarch %{ix86}
cp -r fglrx/common/* fglrx/arch/x86/* fglrxpkg/
%endif

%ifarch x86_64
cp -r fglrx/common/* fglrx/arch/x86_64/* fglrxpkg/
%endif

# proper permissions
find fglrxpkg/lib/modules/fglrx/build_mod/ -type f -print0 | xargs -0 chmod 0644

# debuginfo fix
#sed -i -e 's|strip -g|/bin/true|' fglrxpkg/lib/modules/fglrx/build_mod/make.sh

pushd fglrxpkg
%patch0 -p0 -b.compat_alloc
%patch1 -p0 -b.3.14_kernel
popd

for kernel_version  in %{?kernel_versions} ; do
    cp -a fglrxpkg/  _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    pushd _kmod_build_${kernel_version%%___*}/lib/modules/fglrx/build_mod/2.6.x
    make V=1 CC="gcc" PAGE_ATTR_FIX=0 \
      KVER="${kernel_version%%___*}" \
      KDIR="/usr/src/kernels/${kernel_version%%___*}"
    popd
done


%install
rm -rf $RPM_BUILD_ROOT
for kernel_version in %{?kernel_versions}; do
    install -D -m 0755 _kmod_build_${kernel_version%%___*}/lib/modules/fglrx/build_mod/2.6.x/fglrx.ko $RPM_BUILD_ROOT%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/fglrx.ko
done
%{?akmod_install}


%clean
rm -rf $RPM_BUILD_ROOT


%changelog
* Sat Aug 02 2014 Nicolas Chauvet <kwizart@gmail.com> - 14.4-1.8
- Rebuilt for kernel

* Fri Jul 18 2014 Nicolas Chauvet <kwizart@gmail.com> - 14.4-1.7
- Rebuilt for kernel

* Tue Jul 08 2014 Nicolas Chauvet <kwizart@gmail.com> - 14.4-1.6
- Rebuilt for kernel

* Tue Jun 17 2014 Nicolas Chauvet <kwizart@gmail.com> - 14.4-1.5
- Rebuilt for kernel

* Fri Jun 13 2014 Nicolas Chauvet <kwizart@gmail.com> - 14.4-1.4
- Rebuilt for kernel

* Sun Jun 08 2014 Nicolas Chauvet <kwizart@gmail.com> - 14.4-1.3
- Rebuilt for kernel

* Tue Jun 03 2014 Nicolas Chauvet <kwizart@gmail.com> - 14.4-1.2
- Rebuilt for kernel

* Thu May 15 2014 Nicolas Chauvet <kwizart@gmail.com> - 14.4-1.1
- Rebuilt for kernel

* Mon Apr 28 2014 Leigh Scott <leigh123linux@googlemail.com> - 14.4-1
- Update to Catalyst 14.4  (internal version 14.10.1006)

* Fri Apr 25 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-4.1
- Rebuilt for kernel

* Thu Apr 24 2014 Leigh Scott <leigh123linux@googlemail.com> - 13.9-4
- patch for 3.14 kernel

* Wed Apr 16 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-3.11
- Rebuilt for kernel

* Fri Apr 04 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-3.10
- Rebuilt for kernel

* Wed Apr 02 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-3.9
- Rebuilt for kernel

* Tue Mar 25 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-3.8
- Rebuilt for kernel

* Sun Mar 09 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-3.7
- Rebuilt for kernel

* Wed Mar 05 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-3.6
- Rebuilt for kernel

* Wed Feb 26 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-3.5
- Rebuilt for kernel

* Mon Feb 24 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-3.4
- Rebuilt for kernel

* Thu Feb 20 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-3.3
- Rebuilt for kernel

* Sat Feb 15 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-3.2
- Rebuilt for kernel

* Fri Feb 07 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-3.1
- Rebuilt for kernel

* Thu Jan 30 2014 Leigh Scott <leigh123linux@googlemail.com> - 13.9-3
- patch for 3.13.0 kernel

* Thu Jan 30 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.14
- Rebuilt for kernel

* Tue Jan 28 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.13
- Rebuilt for kernel

* Fri Jan 17 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.12
- Rebuilt for kernel

* Sun Jan 12 2014 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.11
- Rebuilt for kernel

* Wed Dec 25 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.10
- Rebuilt for kernel

* Fri Dec 20 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.9
- Rebuilt for kernel

* Tue Dec 03 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.8
- Rebuilt for kernel

* Thu Nov 21 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.7
- Rebuilt for kernel

* Thu Nov 14 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.6
- Rebuilt for kernel

* Mon Nov 04 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.5
- Rebuilt for kernel

* Mon Nov 04 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.4
- Rebuilt for kernel

* Tue Oct 22 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.3
- Rebuilt for kernel

* Mon Oct 14 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.2
- Rebuilt for kernel

* Fri Oct 11 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.9-2.1
- Rebuilt for kernel

* Fri Oct 04 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.9-1.1
- Rebuilt for kernel

* Thu Oct 03 2013 Leigh Scott <leigh123linux@googlemail.com> - 13.9-1
- Update to Catalyst 13.9  (internal version 13.152)
- redo patch

* Tue Oct 01 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.8-0.2.beta1.8
- Rebuilt for kernel

* Sun Sep 29 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.8-0.2.beta1.7
- Rebuilt for kernel

* Wed Sep 25 2013 Leigh Scott <leigh123linux@googlemail.com> - 13.8-0.2.beta1.6
- Rebuilt for kernel

* Fri Aug 30 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.8-0.2.beta1.5
- Rebuilt for kernel

* Thu Aug 22 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.8-0.2.beta1.4
- Rebuilt for kernel

* Fri Aug 16 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.8-0.2.beta1.3
- Rebuilt for kernel

* Tue Aug 13 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.8-0.2.beta1.2
- Rebuilt for kernel

* Thu Aug 08 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.8-0.2.beta1.1
- Rebuilt for kernel

* Wed Aug 07 2013 Leigh Scott <leigh123linux@googlemail.com> - 13.8-0.2.beta1
- fix proc perms

* Sat Aug 03 2013 Leigh Scott <leigh123linux@googlemail.com> - 13.8-0.1.beta1
- Update to Catalyst 13.8beta1  (internal version 13.20.5)

* Tue Jul 30 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.6-0.1.beta.9
- Rebuilt for kernel

* Fri Jul 26 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.6-0.1.beta.8
- Rebuilt for kernel

* Sat Jul 13 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.6-0.1.beta.7
- Rebuilt for kernel

* Sat Jul 06 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.6-0.1.beta.6
- Rebuilt for kernel

* Sun Jun 30 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.6-0.1.beta.5
- Rebuilt for kernel

* Sat Jun 29 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.6-0.1.beta.4
- Rebuilt for kernel

* Fri Jun 14 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.6-0.1.beta.3
- Rebuilt for current f19 kernel

* Wed Jun 12 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.6-0.1.beta.2
- Rebuilt for current f19 kernel

* Wed Jun 12 2013 Nicolas Chauvet <kwizart@gmail.com> - 13.6-0.1.beta.1
- Rebuilt for kernel

* Wed May 29 2013 Leigh Scott <leigh123linux@googlemail.com> - 13.6-0.1.beta
- Update to Catalyst 13.6beta  (internal version 13.101)

* Thu May 23 2013 Leigh Scott <leigh123linux@googlemail.com> - 13.4-3
- drop intel_iommu patch

* Wed May 22 2013 Leigh Scott <leigh123linux@googlemail.com> - 13.4-2
- Add patch to fix tty issue
- Add patch to fix intel_iommu

* Tue May 14 2013 Leigh Scott <leigh123linux@googlemail.com> - 13.4-1
- Update to Catalyst 13.4 (internal version 12.104)

* Tue May 14 2013 Nicolas Chauvet <kwizart@gmail.com> - 11.11-1.2
- Rebuilt for kernel

* Tue Feb 07 2012 Nicolas Chauvet <kwizart@gmail.com> - 11.11-1.1
- Rebuild for UsrMove

* Wed Nov 16 2011 Stewart Adam <s.adam at diffingo.com> - 11.11-1
- Update to Catalyst 11.11 (internal version 8.91.1)

* Wed Nov 02 2011 Nicolas Chauvet <kwizart@gmail.com> - 11.4-1.5
- Rebuild for F-16 kernel

* Tue Nov 01 2011 Nicolas Chauvet <kwizart@gmail.com> - 11.4-1.4
- Rebuild for F-16 kernel

* Fri Oct 28 2011 Nicolas Chauvet <kwizart@gmail.com> - 11.4-1.3
- Rebuild for F-16 kernel

* Sun Oct 23 2011 Nicolas Chauvet <kwizart@gmail.com> - 11.4-1.2
- Rebuild for F-16 kernel

* Sat May 28 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 11.4-1.1
- rebuild for F15 release kernel

* Mon May 2 2011 Stewart Adam <s.adam at diffingo.com> 11.4-1
- Update to Catalyst 11.4 (internal version 8.84.1)
- Sync with F-14 branch

* Sun Apr 24 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 11.2-1.2
- rebuild for updated kernel

* Mon Apr 04 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 11.2-1.1
- rebuild for updated kernel

* Sat Feb 19 2011 Stewart Adam <s.adam at diffingo.com> - 11.2-1
- Update to Catalyst 11.2 (internal version 8.82.1)

* Sat Feb 12 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.12-1.1
- rebuild for updated kernel

* Sun Dec 26 2010 Stewart Adam <s.adam at diffingo.com> - 10.12-1
- Update to Catalyst 10.12 (internal version 8.80.1)
- Merge changes from F-13 branch

* Fri Dec 17 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.11-1.2
- rebuild for updated kernel

* Tue Dec 07 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.11-1.1
- rebuild for F-14 kernel

* Sat Nov 20 2010 Stewart Adam <s.adam at diffingo.com> - 10.11-1
- Update to Catalyst 10.11 (internal version 8.79.1)

* Mon Oct 25 2010 Stewart Adam <s.adam at diffingo.com> - 10.10-1
- Update to Catalyst 10.10 (internal version 8.78.3)

* Thu Oct 21 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.9-1.2
- rebuild for new kernel

* Sun Sep 19 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.9-1.1
- rebuild for new kernel

* Sat Sep 18 2010 Stewart Adam <s.adam at diffingo.com>	- 10.9-1
- Update to Catalyst 10.9 (internal version 8.77.1)

* Sat Sep 11 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.8-1.2
- rebuild for new kernel

* Fri Sep 10 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.8-1.1
- rebuild for new kernel

* Mon Aug 30 2010 Stewart Adam <s.adam at diffingo.com> - 10.8-1
- Update to 10.8 (internal version 8.76.2)

* Sat Aug 28 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.7-1.4
- rebuild for new kernel

* Fri Aug 20 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.7-1.3
- rebuild for new kernel

* Wed Aug 11 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.7-1.2
- rebuild for new kernel

* Sun Aug 08 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.7-1.1
- rebuild for new kernel

* Wed Jul 28 2010 Stewart Adam <s.adam at diffingo.com> - 10.7-1
- Update to Catalyst 10.7 (internal version 8.75.3)
- Synchronize changes with those in F-12 branch

* Tue Jul 27 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.5-1.4
- rebuild for new kernel

* Wed Jul 07 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.5-1.3
- rebuild for new kernel

* Fri Jun 18 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.5-1.2
- rebuild for new kernel

* Tue Jun 1 2010 Stewart Adam <s.adam at diffingo.com> - 10.5-1.1
- Rebuild with correct sources

* Thu May 27 2010 Stewart Adam <s.adam at diffingo.com> - 10.5-1
- Update to Catalyst 10.5 (internal version 8.73.2)

* Sat May 1 2010 Stewart Adam <s.adam at diffingo.com> - 10.4-1
- Update to Catalyst 10.4 (internal version 8.72.3)

* Thu Feb 11 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.1-1.3
- rebuild for new kernel

* Mon Feb 08 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.1-1.2
- rebuild for new kernel

* Thu Feb 04 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 10.1-1.1
- rebuild for new kernel

* Wed Jan 27 2010 Stewart Adam <s.adam at diffingo.com> - 10.1-1
- Update to Catalyst 10.1 (internal version 8.69)

* Fri Jan 22 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.12-1.1
- rebuild for new kernel

* Mon Dec 28 2009 Stewart Adam <s.adam at diffingo.com> - 9.12-1
- Update to Catalyst 9.12 (internal version 8.68.1)

* Sat Dec 26 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.10-1.4
- rebuild for new kernel

* Sun Dec 06 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.10-1.3
- rebuild for new kernel

* Sun Nov 22 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.10-1.2
- rebuild for new kernels

* Thu Nov 05 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.10-1.1
- rebuild for new kernels

* Sat Oct 24 2009 Stewart Adam <s.adam at diffingo.com>	- 9.10-1
- Update to Catalyst 9.10 (internal version 8.66.1)

* Tue Oct 20 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.9-1.2
- rebuild for new kernels

* Wed Sep 30 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.9-1.1
- rebuild for new kernels

* Fri Sep 11 2009 Stewart Adam <s.adam at diffingo.com> - 9.9-1
- Update to Catalyst 9.9 (internal version 8.65.4)

* Tue Sep 01 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.8-1.4
- rebuild for new kernels

* Thu Aug 27 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.8-1.3
- rebuild for new kernels

* Sun Aug 23 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.8-1.2
- rebuild for new kernels

* Sat Aug 22 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.8-1.1
- rebuild for new kernels

* Wed Aug 19 2009 Stewart Adam <s.adam at diffingo.com> - 9.8-1
- Update to Catalyst 9.8 (internal version 8.64.3)

* Sat Aug 15 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.5-1.8
- rebuild for new kernels

* Tue Aug 04 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.5-1.7
- rebuild for new kernels

* Tue Jul 14 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.5-1.6
- rebuild for new kernels

* Mon Jun 22 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.5-1.5
- rebuild for new kernels

* Fri Jun 19 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.5-1.4
- rebuild for new kernels

* Wed May 27 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.5-1.3
- rebuild for new kernels

* Sun May 24 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.5-1.2
- rebuild for new kernels

* Thu May 21 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.5-1.1
- rebuild for new kernels

* Thu May 21 2009 kwizart < kwizart at gmail.com > - 9.5-1
- Update to 9.5 (internal version 8.612)

* Thu May 21 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.4-2.2
- rebuild for new kernels

* Wed May 13 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.4-2.1
- rebuild for new kernels

* Wed May 6 2009 Stewart Adam <s.adam at diffingo.com> - 9.4-2
- Remove Makefile patch and set KDIR variable instead (thanks to kwizart)

* Sat Apr 18 2009 Stewart Adam <s.adam at diffingo.com> - 9.4-1
- Update to 9.4
- Fork as catalyst-kmod

* Sun Apr 05 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.4-0.2.beta.1
- rebuild for new kernels

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 9.4-0.2.beta
- rebuild for new F11 features

* Sat Mar 28 2009 Stewart Adam <s.adam at diffingo.com> - 9.4-0.1.beta
- Update to Catalyst 9.4 (beta)

* Sat Mar 28 2009 Stewart Adam <s.adam at diffingo.com> - 9.3-1
- Update to Catalyst 9.3

* Sat Feb 21 2009 Stewart Adam <s.adam at diffingo.com> - 9.2-2
- Fix flush_tlb_page modprobe errors on x86_64

* Fri Feb 20 2009 Stewart Adam <s.adam at diffingo.com> - 9.2-1
- Update to Catalyst 9.2
- Use Catalyst version for Version tag instead of internal driver version

* Sun Feb 15 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 8.573-1.9.1.2
- rebuild for latest Fedora kernel;

* Sun Feb 01 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 8.573-1.9.1.1
- rebuild for latest Fedora kernel;

* Sat Jan 31 2009 Stewart Adam <s.adam at diffingo.com> - 8.573-1.9.1
- Update to Catalyst 9.1

* Sun Jan 25 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 8.561-2.8.12.6
- rebuild for latest Fedora kernel;

* Sun Jan 18 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 8.561-2.8.12.5
- rebuild for latest Fedora kernel;

* Sun Jan 11 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 8.561-2.8.12.4
- rebuild for latest Fedora kernel;

* Sun Jan 04 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 8.561-2.8.12.3
- rebuild for latest Fedora kernel;

