#!/bin/sh

set -x
intltoolize --force || exit 1
autoconf || exit 1
automake --add-missing --foreign || exit 1
