{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-25.11";
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
              python310
              ruff
              uv
              pre-commit
              nil
            ];

          shellHook = ''
            VENV_PATH=.venv
            NEEDS_VENV=0

            if test ! -d $VENV_PATH; then
              NEEDS_VENV=1
            else
              NIX_PYTHON=$(python3 --version)
              VENV_PYTHON=$(.venv/bin/python3 --version 2>/dev/null || echo "")
              if [ "$NIX_PYTHON" != "$VENV_PYTHON" ]; then
                NEEDS_VENV=1
              fi
            fi

            if [ "$NEEDS_VENV" = "1" ]; then
              uv venv --clear --offline --python $(which python3) $VENV_PATH
            fi
          '';
        };
      });
    };
}
