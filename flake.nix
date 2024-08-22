{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
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
          packages = with pkgs; [
              python39
              ruff
              uv
            ];

          shellHook = ''
            VENV=.venv

            if test -d $VENV; then
              NIX_PYTHON=$(python3 --version)
              VENV_PYTHON=$(.venv/bin/python3 --version)
              if [ "$NIX_PYTHON" != "$VENV_PYTHON" ]; then
                rm -rf $VENV
              fi
            fi

            if test ! -d $VENV; then
              uv venv --offline --python $(which python3) $VENV
            fi
          '';
        };
      });
    };
}
