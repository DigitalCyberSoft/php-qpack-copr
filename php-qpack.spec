# we dont want -z defs linker flag
%undefine _strict_symbol_defs_build

%global pecl_name   qpack
%global with_zts    0%{!?_without_zts:%{?__ztsphp:1}}
%global ini_name    40-%{pecl_name}.ini

# Latest release version - update this to build a new version
%global upstream_version 1.0.1

Name:           php-%{pecl_name}
Version:        %{upstream_version}
Release:        1%{?dist}
Summary:        QPACK header compression extension for PHP (RFC 9204)

License:        MIT
URL:            https://github.com/DigitalCyberSoft/php-qpack
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz#/php-qpack-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  php-devel >= 8.0

Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}

%description
PHP extension for QPACK header compression as defined in RFC 9204.
QPACK is the header compression format used by HTTP/3.

Includes a built-in pure C implementation of QPACK with the complete
RFC 9204 static table (99 entries), dynamic table management, encoder
stream processing, and standalone Huffman encoding/decoding functions.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       php-devel%{?_isa}

%description devel
These are the files needed to compile programs using %{name}.

%prep
%setup -q -n php-qpack-%{version}

# Sanity check
extver=$(sed -n '/#define PHP_QPACK_VERSION/{s/.* "//;s/".*$//;p}' php_qpack.h)
if test "x${extver}" != "x%{version}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}.
   exit 1
fi

%if %{with_zts}
# Duplicate for ZTS build
cp -pr . ../ZTS
%endif

%build
# NTS build
%{_bindir}/phpize
%configure \
    --with-php-config=%{_bindir}/php-config \
    --with-libdir=%{_lib} \
    --enable-qpack

make %{?_smp_mflags}

%if %{with_zts}
# ZTS build
cd ../ZTS
%{_bindir}/zts-phpize
%configure \
    --with-php-config=%{_bindir}/zts-php-config \
    --with-libdir=%{_lib} \
    --enable-qpack

make %{?_smp_mflags}
%endif

%install
# Install NTS extension
make install INSTALL_ROOT=%{buildroot}

# Install config file
install -d %{buildroot}%{php_inidir}
cat > %{buildroot}%{php_inidir}/%{ini_name} << EOF
; Enable qpack extension module
extension = %{pecl_name}.so
EOF

%if %{with_zts}
# Install ZTS extension
cd ../ZTS
make install INSTALL_ROOT=%{buildroot}

# Install ZTS config file
install -d %{buildroot}%{php_ztsinidir}
cp %{buildroot}%{php_inidir}/%{ini_name} \
   %{buildroot}%{php_ztsinidir}/%{ini_name}
%else
# Remove any ZTS files that NTS make install may have created
find %{buildroot} -name "%{pecl_name}.so" -not -path "%{buildroot}%{php_extdir}/*" -delete 2>/dev/null || :
%endif

# Install headers for devel package
install -d %{buildroot}%{php_incldir}/ext/%{pecl_name}
cp -p php_qpack.h %{buildroot}%{php_incldir}/ext/%{pecl_name}/

%check
# Minimal load test for NTS extension
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep "^%{pecl_name}$"

# Upstream test suite for NTS extension
TEST_PHP_EXECUTABLE=%{__php} \
TEST_PHP_ARGS="-n -d extension=%{buildroot}%{php_extdir}/%{pecl_name}.so" \
REPORT_EXIT_STATUS=1 \
%{__php} -n run-tests.php -q --show-diff

%if %{with_zts}
# Minimal load test for ZTS extension
%{__ztsphp} --no-php-ini \
    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep "^%{pecl_name}$"

# Upstream test suite for ZTS extension
cd ../ZTS
TEST_PHP_EXECUTABLE=%{__ztsphp} \
TEST_PHP_ARGS="-n -d extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so" \
REPORT_EXIT_STATUS=1 \
%{__ztsphp} -n run-tests.php -q --show-diff
%endif

%files
%license LICENSE
%doc README.md
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif

%files devel
%{php_incldir}/ext/%{pecl_name}

%changelog
* Sat Mar 14 2026 James Campbell - 1.0.1-1
- Version bump to 1.0.1

* Fri Mar 13 2026 James Campbell - 1.0.0-1
- Initial package
- QPACK header compression for HTTP/3 (RFC 9204)
- Built-in pure C implementation, no external dependencies
- Supports both NTS and ZTS builds
