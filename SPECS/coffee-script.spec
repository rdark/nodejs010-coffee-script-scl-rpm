%{?scl:%scl_package coffee-script}
%{!?scl:%global pkg_name %{name}}

%{?nodejs_find_provides_and_requires}

# This package is different from most node packages in Fedora because
# CoffeeScript is written in itself, and per Fedora policy we need to compile
# it--we can't ship the precompiled version.

# don't build the minified browser version yet since uglify-js isn't in the distro
%global enable_minified 0

%define     shortname   coffeescript

# %global commit 84b8b5cceef6c452996d022c4c2d47dc8c8a5ccc
# %global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:       %{?scl_prefix}coffee-script
Version:    1.6.3
Release:    2%{?dist}
Summary:    A programming language that transcompiles to JavaScript
License:    MIT
Group:      Development/Languages
URL:        http://coffeescript.org/
Source0:    https://github.com/jashkenas/coffee-script/archive/%{version}.tar.gz
BuildRoot:  %{_tmppath}/%{pkg_name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:  noarch
ExclusiveArch: %{ix86} x86_64 %{arm} noarch

# some fixes for Cakefile, including:
#  - follow FHS and Fedora Node.js packaging guidelines
#  - support DESTDIR
#  - preserve timestamps when installing
Patch1:     coffee-script-Cakefile.patch

# upstream patches to fix one broken test
# https://github.com/jashkenas/coffee-script/commit/2e408648aad42901d96df01fe8475a18054e32c2
Patch2:     coffee-script-fix-importing-test.patch

BuildRequires: %{?scl_prefix}nodejs-devel
BuildRequires: %{?scl_prefix}nodejs
BuildRequires: %{?scl_prefix}build
BuildRequires: %{?scl_prefix}runtime
Requires:   %{?scl_prefix}runtime
Requires:   %{?scl_prefix}%{pkg_name}-common == %{version}-%{release}

%if 0%{?enable_minified}
BuildRequires: %{?scl_prefix}npm(uglify-js)
%endif

%description
CoffeeScript is a little language that compiles into JavaScript. Underneath all
of those embarrassing braces and semicolons, JavaScript has always had a
gorgeous object model at its heart. CoffeeScript is an attempt to expose the
good parts of JavaScript in a simple way.

The golden rule of CoffeeScript is: "It's just JavaScript". The code compiles
one-to-one into the equivalent JS, and there is no interpretation at runtime.
You can use any existing JavaScript library seamlessly (and vice-versa). The
compiled output is readable and pretty-printed, passes through JavaScript Lint
without warnings, will work in every JavaScript implementation, and tends to run
as fast or faster than the equivalent handwritten JavaScript.

%package common
Summary: A programming that transcompiles to JavaScript - core compiler
Group: Development/Languages

%description common
This is the core compiler for the CoffeeScript language, suitable for use in
browsers or by other JavaScript implementations.

For the primary compiler and cake utility used in conjunction with Node.js,
install the 'coffee-script' package.

%package doc
Summary: A programming language that transcompiles to JavaScript - documentation
Group: Documentation

%description doc
The documentation for the CoffeeScript programming language.

%prep
%setup -n %{pkg_name}-%{version} -qn %{shortname}-%{version}
%patch1
%patch2 -p1

#rename documentation directory to html cause that's what we want in %%doc
mv documentation html

%build
%{?scl:scl enable %{scl} - << \EOF}
./bin/cake build
%{?scl:EOF}
%if 0%{?enable_minified}
#build the minified coffee-script browser version and put it in its place
%{?scl:scl enable %{scl} - << \EOF}
./bin/cake build:browser
%{?scl:EOF}
mv extras/coffee-script.js extras/coffee-script.min.js
%endif

#also build the unminifed version
%{?scl:scl enable %{scl} - << \EOF}
MINIFY=false ./bin/cake build:browser
%{?scl:EOF}

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_datadir}/%{pkg_name}/
cp -pr lib extras %{buildroot}%{_datadir}/%{pkg_name}/
chmod 0644 %{buildroot}%{_datadir}/%{pkg_name}/lib/coffee-script/parser.js

mkdir -p %{buildroot}%{nodejs_sitelib}/%{pkg_name}
cp -pr bin package.json %{buildroot}%{nodejs_sitelib}/%{pkg_name}
ln -sf %{_datadir}/%{pkg_name}/lib %{buildroot}%{nodejs_sitelib}/%{pkg_name}/lib
ln -sf %{_datadir}/%{pkg_name}/extras %{buildroot}%{nodejs_sitelib}/%{pkg_name}/extras

mkdir -p %{buildroot}%{_bindir}
ln -sf ../lib/node_modules/%{pkg_name}/bin/coffee %{buildroot}%{_bindir}/coffee
ln -sf ../lib/node_modules/%{pkg_name}/bin/cake %{buildroot}%{_bindir}/cake

#we skip %%nodejs_symlink_deps because this package has no dependencies, and if
#it did, would need special treatment anyway

%check
# tests pass but something weird is going on with node itself at the end
%{?scl:scl enable %{scl} - << \EOF}
./bin/cake test || :
%{?scl:EOF}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{nodejs_sitelib}/%{pkg_name}
%{_bindir}/coffee
%{_bindir}/cake

%files common
%defattr(-,root,root,-)
%{_datadir}/%{pkg_name}
%doc README LICENSE

%files doc
%defattr(-,root,root,-)
%doc html

%changelog
* Fri Sep 05 2014 Richard Clark <rclark@telnic.org> - 1.6.3-2
- Rebuild for SCL

* Wed Jun 19 2013 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1.6.3-1
- new upstream release 1.6.3
  http://coffeescript.org/#changelog
- restrict to the architectures node works on
- add EPEL6 dependency generation macro

* Sun Feb 10 2013 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1.4.0-4
- fix rpmlint warnings
- rename documentation subpackage to "coffee-script-doc"

* Fri Feb 01 2013 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1.4.0-3
- rearrange symlinks to dep/provides generation works
- conditionalize minification so it works in the absence of uglify-js

* Thu Jan 31 2013 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1.4.0-2
- provide a -common subpackage with stuff useful for other JS runtimes/browsers
- split off the docs too

* Tue Jan 15 2013 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1.4.0-1
- new upstream release 1.4.0
- clean up for submission

* Sat Aug 20 2011 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1.1.2-1
- initial package
