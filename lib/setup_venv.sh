#!/bin/bash

set -euo pipefail

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

declare -a APT_PACKAGES=("build-essential" "python3-venv" "python3-dev")

virualenv_dir="${HOME}/.cache/venv/mikrotik-tools-py3"

if [ ! -e "${virualenv_dir}/bin/activate" ]; then
  echo "Python 3 virtual environment needs to be created for this script to run"
  read -p "Do you want to setup a venv now? [Y/n] " -r
  if [[ ! $REPLY =~ ^([yY][eE][sS]|[yY]|)$ ]]; then exit 1 ; fi

  echo "Updating lists of packages"
  sudo -- sh -c '/usr/bin/apt-get -qq update'
  all_pkgs_installed=true
  for pkg in "${APT_PACKAGES[@]}"
  do
    if ! dpkg-query -Wf'${db:Status-abbrev}' "${pkg}" 2>/dev/null | grep -q '^.i'; then
      echo "  ${pkg} package is not installed"
      all_pkgs_installed=false
    fi
  done
  if [ ! "$all_pkgs_installed" = true ] ; then
    PKGS="${APT_PACKAGES[@]}"
    echo "About to install the following packages: ${PKGS}"
    sudo apt install ${PKGS}
  fi

  python3 -m venv "${virualenv_dir}"
  . "${virualenv_dir}/bin/activate"
  pip3 install wheel
  pip3 install --upgrade pip
  pip3 install -r "${script_dir}/requirements.txt"
  # deactivate fails with -eu options set
  # https://github.com/pypa/virtualenv/issues/1342
  set +eu
  deactivate
  set -eu
fi