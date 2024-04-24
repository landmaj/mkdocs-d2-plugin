{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
  };

  outputs =
    { self, nixpkgs }:
    let
      forAllSystems = function:
        nixpkgs.lib.genAttrs [
          "x86_64-linux"
          "x86_64-darwin"
          "aarch64-linux"
          "aarch64-darwin"
        ]
          (system: function nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs;
            let
              # CHANGE PYTHON VERSION
              devpython = python3.withPackages
                (packages: with packages; [
                  # PYTHON PACKAGES
                  virtualenv
                  pip
                  setuptools
                  wheel
                ]);
            in
            [
              # SYSTEM PACKAGES
              devpython
            ];

          shellHook = ''
            # Setup the virtual environment if it doesn't already exist.
            VENV=.venv
            if test ! -d $VENV; then
              virtualenv $VENV
            fi

            # Check if Python version in virtualenv is correct
            NIX_PYTHON=$(python3 --version)
            VENV_PYTHON=$(.venv/bin/python3 --version)
            if [ "$NIX_PYTHON" != "$VENV_PYTHON" ]; then
              echo -e "\033[0;31m!!! INCORRECT PYTHON VERSION IN VIRTUALENV !!!\033[0m"
            fi
          '';
        };
      });
    };
}
