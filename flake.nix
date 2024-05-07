{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-23.11";
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
              # PYTHON VERSION
              devpython = python39.withPackages
                (packages: with packages; [
                  # PYTHON PACKAGES
                  virtualenv
                ]);
            in
            [
              # SYSTEM PACKAGES
              devpython
            ];

          shellHook = ''
            # check if Python version in virtualenv is correct
            if test -d $VENV; then
              NIX_PYTHON=$(python3 --version)
              VENV_PYTHON=$(.venv/bin/python3 --version)
              if [ "$NIX_PYTHON" != "$VENV_PYTHON" ]; then
                echo -e "\033[0;31m!!! INCORRECT PYTHON VERSION IN VIRTUALENV !!!\033[0m"
                rm -rf $VENV
              fi
            fi

            # setup the virtual environment if it doesn't exist
            VENV=.venv
            if test ! -d $VENV; then
              virtualenv $VENV
              $VENV/bin/pip install --upgrade pip build twine
            fi
          '';
        };
      });
    };
}
