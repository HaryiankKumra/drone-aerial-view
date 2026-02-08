{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.virtualenv
    pkgs.gcc
    pkgs.cmake
    pkgs.pkg-config
  ];
}
