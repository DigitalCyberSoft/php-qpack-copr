# PHP-QPACK COPR Build Repository

Automated COPR build configuration for [php-qpack](https://github.com/DigitalCyberSoft/php-qpack) - PHP extension for QPACK header compression (RFC 9204).

## Overview

This repository contains the COPR build configuration to automatically build RPM packages for the PHP QPACK extension from GitHub releases.

## Features

- **Automated Builds**: Builds directly from php-qpack GitHub releases
- **PHP Version Support**: Builds for the system PHP version (8.0+)
- **NTS and ZTS Support**: Builds both non-thread-safe and thread-safe variants
- **Zero External Dependencies**: Uses built-in pure C QPACK implementation
- **Test Suite**: Runs upstream test suite during build

## COPR Repository

The built packages are available in COPR at:
```
https://copr.fedorainfracloud.org/coprs/reversejames/php-qpack/
```

### Installation

```bash
# Enable the COPR repository
sudo dnf copr enable reversejames/php-qpack

# Install php-qpack
sudo dnf install php-qpack

# For development headers
sudo dnf install php-qpack-devel

# Restart PHP-FPM if using it
sudo systemctl restart php-fpm
```

## Configuration

The extension is configured via `/etc/php.d/40-qpack.ini`:
```ini
; Enable qpack extension module
extension = qpack.so
```

## Verification

```bash
php -m | grep qpack
php -i | grep qpack
```

## Build Process

1. Downloads the php-qpack source from GitHub release tag
2. Validates version against `php_qpack.h`
3. Generates RPM spec file dynamically
4. Builds SRPM for COPR

## Local Testing

```bash
cd .copr
make srpm
```

## Dependencies

- **Build**: gcc, make, php-devel (>= 8.0)
- **Runtime**: php

## Extension Features

- QPACK header compression/decompression (RFC 9204)
- QPackContext class with dynamic table management
- Complete 99-entry static table (RFC 9204 Appendix A)
- Encoder stream processing
- Standalone Huffman encode/decode functions

## License

The build configuration is provided as-is. php-qpack is licensed under the MIT License.

## Upstream

- php-qpack GitHub: https://github.com/DigitalCyberSoft/php-qpack
- RFC 9204 (QPACK): https://www.rfc-editor.org/rfc/rfc9204
