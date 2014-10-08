%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%define _project yconfig

Name:    python-%{_project}
Version: 0.2
Release: 1%{?dist}
Summary: Yet Another YAML configuration files manager for python

Group:   Development/Languages
License: BSD
URL:     http://github.com/jet9/%{name}
Source:  http://pypi.python.org/packages/source/y/%{_project}/%{_project}-%{version}.tar.gz
Vendor:  Jet9

BuildArch:     noarch

%description
Yet Another YAML configuration files manager for python


%prep
%setup -n %{_project}-%version -q


%build
%{__python} setup.py build


%install
[ "%buildroot" = "/" ] || rm -rf "%buildroot"

%{__python} setup.py install -O1 --skip-build --root "%buildroot"


%files
%define _unpackaged_files_terminate_build 0
%defattr(-,root,root,-)

%python_sitelib/yconfig.py
%python_sitelib/%{_project}-*.egg-info


%clean
[ "%buildroot" = "/" ] || rm -rf "%buildroot"


%changelog
* Wed Oct 08 2014 Dmitry Kurbatov <dk@dimcha.ru> - 0.2
- create custom spec file