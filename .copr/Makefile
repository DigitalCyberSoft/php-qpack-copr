# COPR Makefile for automated php-qpack builds
# Downloads php-qpack from GitHub and builds PHP extension

# COPR provides outdir, set default for local testing
outdir ?= .

# Fetch latest release version from GitHub
QPACK_VERSION := $(shell curl -s https://api.github.com/repos/DigitalCyberSoft/php-qpack/releases/latest | sed -n 's/.*"tag_name": *"v\?\([^"]*\)".*/\1/p')
QPACK_URL = https://github.com/DigitalCyberSoft/php-qpack/archive/refs/tags/v$(QPACK_VERSION).tar.gz

# Default target for COPR
srpm:
	@echo "=== Starting php-qpack SRPM build ==="
	@echo "Output directory: $(outdir)"
	@echo "Working directory: $$(pwd)"

	# Install php-devel for phpize and php-config
	dnf -y install php-devel

	# Download php-qpack source
	@echo "=== Downloading php-qpack $(QPACK_VERSION) ==="
	curl -L -o php-qpack-$(QPACK_VERSION).tar.gz $(QPACK_URL) || exit 1

	# Get PHP version from php-config
	PHP_VER=$$(php-config --version); echo "  PHP version: $$PHP_VER"

	# Generate spec file
	@echo "=== Generating spec file ==="
	@PHP_VER=$$(php-config --version); \
	( \
	echo '# we dont want -z defs linker flag'; \
	echo '%undefine _strict_symbol_defs_build'; \
	echo ''; \
	echo '%global pecl_name   qpack'; \
	echo '%global with_zts    0%{!?_without_zts:%{?__ztsphp:1}}'; \
	echo '%global ini_name    40-%{pecl_name}.ini'; \
	echo ''; \
	echo 'Name:           php-%{pecl_name}'; \
	echo 'Version:        $(QPACK_VERSION)'; \
	echo "Release:        1.php$${PHP_VER}%{?dist}"; \
	echo 'Summary:        QPACK header compression extension for PHP (RFC 9204)'; \
	echo ''; \
	echo 'License:        MIT'; \
	echo 'URL:            https://github.com/DigitalCyberSoft/php-qpack'; \
	echo 'Source0:        php-qpack-%{version}.tar.gz'; \
	echo ''; \
	echo 'BuildRequires:  gcc'; \
	echo 'BuildRequires:  make'; \
	echo 'BuildRequires:  php-devel >= 8.0'; \
	echo ''; \
	echo 'Requires:       php(zend-abi) = %{php_zend_api}'; \
	echo 'Requires:       php(api) = %{php_core_api}'; \
	echo ''; \
	echo '%description'; \
	echo 'PHP extension for QPACK header compression as defined in RFC 9204.'; \
	echo 'QPACK is the header compression format used by HTTP/3.'; \
	echo ''; \
	echo 'Includes a built-in pure C implementation of QPACK with the complete'; \
	echo 'RFC 9204 static table (99 entries), dynamic table management, encoder'; \
	echo 'stream processing, and standalone Huffman encoding/decoding functions.'; \
	echo ''; \
	echo '%package devel'; \
	echo 'Summary:        Development files for %{name}'; \
	echo 'Requires:       %{name}%{?_isa} = %{version}-%{release}'; \
	echo 'Requires:       php-devel%{?_isa}'; \
	echo ''; \
	echo '%description devel'; \
	echo 'These are the files needed to compile programs using %{name}.'; \
	echo ''; \
	echo '%prep'; \
	echo '%setup -q -n php-qpack-%{version}'; \
	echo ''; \
	echo '# Sanity check'; \
	echo 'extver=$$(sed -n '"'"'/#define PHP_QPACK_VERSION/{s/.* "//;s/".*$$//;p}'"'"' php_qpack.h)'; \
	echo 'if test "x$${extver}" != "x%{version}"; then'; \
	echo '   : Error: Upstream extension version is $${extver}, expecting %{version}.'; \
	echo '   exit 1'; \
	echo 'fi'; \
	echo ''; \
	echo '%if %{with_zts}'; \
	echo '# Duplicate for ZTS build'; \
	echo 'cp -pr . ../ZTS'; \
	echo '%endif'; \
	echo ''; \
	echo '%build'; \
	echo '# NTS build'; \
	echo '%{_bindir}/phpize'; \
	echo '%configure \'; \
	echo '    --with-php-config=%{_bindir}/php-config \'; \
	echo '    --with-libdir=%{_lib} \'; \
	echo '    --enable-qpack'; \
	echo ''; \
	echo 'make %{?_smp_mflags}'; \
	echo ''; \
	echo '%if %{with_zts}'; \
	echo '# ZTS build'; \
	echo 'cd ../ZTS'; \
	echo '%{_bindir}/zts-phpize'; \
	echo '%configure \'; \
	echo '    --with-php-config=%{_bindir}/zts-php-config \'; \
	echo '    --with-libdir=%{_lib} \'; \
	echo '    --enable-qpack'; \
	echo ''; \
	echo 'make %{?_smp_mflags}'; \
	echo '%endif'; \
	echo ''; \
	echo '%install'; \
	echo '# Install NTS extension'; \
	echo 'make install INSTALL_ROOT=%{buildroot}'; \
	echo ''; \
	echo '# Install config file'; \
	echo 'install -d %{buildroot}%{php_inidir}'; \
	echo 'cat > %{buildroot}%{php_inidir}/%{ini_name} << EOF'; \
	echo '; Enable qpack extension module'; \
	echo 'extension = %{pecl_name}.so'; \
	echo 'EOF'; \
	echo ''; \
	echo '%if %{with_zts}'; \
	echo '# Install ZTS extension'; \
	echo 'cd ../ZTS'; \
	echo 'make install INSTALL_ROOT=%{buildroot}'; \
	echo ''; \
	echo '# Install ZTS config file'; \
	echo 'install -d %{buildroot}%{php_ztsinidir}'; \
	echo 'cp %{buildroot}%{php_inidir}/%{ini_name} \'; \
	echo '   %{buildroot}%{php_ztsinidir}/%{ini_name}'; \
	echo '%else'; \
	echo '# Remove any ZTS files that NTS make install may have created'; \
	echo 'find %{buildroot} -name "%{pecl_name}.so" -not -path "%{buildroot}%{php_extdir}/*" -delete 2>/dev/null || :'; \
	echo '%endif'; \
	echo ''; \
	echo '# Install headers for devel package'; \
	echo 'install -d %{buildroot}%{php_incldir}/ext/%{pecl_name}'; \
	echo 'cp -p php_qpack.h %{buildroot}%{php_incldir}/ext/%{pecl_name}/'; \
	echo ''; \
	echo '%check'; \
	echo '# Minimal load test for NTS extension'; \
	echo '%{__php} --no-php-ini \'; \
	echo '    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \'; \
	echo '    --modules | grep "^%{pecl_name}$$"'; \
	echo ''; \
	echo '# Upstream test suite for NTS extension'; \
	echo 'TEST_PHP_EXECUTABLE=%{__php} \'; \
	echo 'TEST_PHP_ARGS="-n -d extension=%{buildroot}%{php_extdir}/%{pecl_name}.so" \'; \
	echo 'REPORT_EXIT_STATUS=1 \'; \
	echo '%{__php} -n run-tests.php -q --show-diff'; \
	echo ''; \
	echo '%if %{with_zts}'; \
	echo '# Minimal load test for ZTS extension'; \
	echo '%{__ztsphp} --no-php-ini \'; \
	echo '    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \'; \
	echo '    --modules | grep "^%{pecl_name}$$"'; \
	echo ''; \
	echo '# Upstream test suite for ZTS extension'; \
	echo 'cd ../ZTS'; \
	echo 'TEST_PHP_EXECUTABLE=%{__ztsphp} \'; \
	echo 'TEST_PHP_ARGS="-n -d extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so" \'; \
	echo 'REPORT_EXIT_STATUS=1 \'; \
	echo '%{__ztsphp} -n run-tests.php -q --show-diff'; \
	echo '%endif'; \
	echo ''; \
	echo '%files'; \
	echo '%license LICENSE'; \
	echo '%doc README.md'; \
	echo '%config(noreplace) %{php_inidir}/%{ini_name}'; \
	echo '%{php_extdir}/%{pecl_name}.so'; \
	echo ''; \
	echo '%if %{with_zts}'; \
	echo '%config(noreplace) %{php_ztsinidir}/%{ini_name}'; \
	echo '%{php_ztsextdir}/%{pecl_name}.so'; \
	echo '%endif'; \
	echo ''; \
	echo '%files devel'; \
	echo '%{php_incldir}/ext/%{pecl_name}'; \
	echo ''; \
	echo '%changelog'; \
	echo "* $$(date '+%a %b %d %Y') COPR Builder - $(QPACK_VERSION)-1"; \
	echo '- Automated build from GitHub release $(QPACK_VERSION)'; \
	echo '- QPACK header compression for HTTP/3 (RFC 9204)'; \
	echo '- Supports both NTS and ZTS builds'; \
	) > php-qpack.spec || exit 1

	@echo "Spec file generated"

	# Build SRPM
	@echo "=== Building SRPM ==="
	rpmbuild -bs \
		--define "_sourcedir $$(pwd)" \
		--define "_specdir $$(pwd)" \
		--define "_builddir $$(pwd)" \
		--define "_srcrpmdir $(outdir)" \
		--define "_rpmdir $$(pwd)" \
		php-qpack.spec || exit 1

	@echo "=== SRPM build complete ==="
	ls -la $(outdir)/*.src.rpm

clean:
	@rm -f *.tar.gz *.spec *.src.rpm
	@rm -rf php-qpack-*/

.PHONY: srpm clean
