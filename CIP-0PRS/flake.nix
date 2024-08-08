{
  description = "Peras Specification";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/cb9a96f23c491c081b38eab96d22fa958043c9fa";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = import nixpkgs { inherit system; };
          lib = pkgs.stdEnv.lib;
          localEmacs = (pkgs.emacs.pkgs.withPackages (epkgs: (with epkgs.melpaStablePackages; [
            epkgs.agda2-mode
          ])));
          agda-stdlib = pkgs.agdaPackages.standard-library.overrideAttrs (oldAtts: rec {
            version = "2.0";
            src = pkgs.fetchFromGitHub {
              repo = "agda-stdlib";
              owner = "agda";
              rev = "v${version}";
              sha256 = "sha256-TjGvY3eqpF+DDwatT7A78flyPcTkcLHQ1xcg+MKgCoE=";
            };
            preConfigure = ''
              runhaskell GenerateEverything.hs
              rm EverythingSafe.agda
            '';
          });
          iog-prelude = pkgs.agdaPackages.mkDerivation {
            pname = "iog-prelude";
            version = "0.1";
            meta = { };
            src = pkgs.fetchFromGitHub {
              repo = "iog-agda-prelude";
              owner = "functionally";
              rev = "2b780014456447bfe2a936be04a0e06f3f1ebba8";
              sha256 = "sha256-z3Or2gPin7fZzVkIhEkRVu8+KFxjNfKh6Ik5sM7qqks=";
            };
            preConfigure = ''
              echo "module Everything where" > Everything.agda
              find src -type f | sed -e '/Dec\.agda$/d;s@^src/\(.*\)\.agda$@open import \1@;s@/@.@g' >> Everything.agda
            '';
            buildInputs = [ agda-stdlib ];
          };
          localAgda = pkgs.agda.withPackages (ps: [
            agda-stdlib
            iog-prelude
          ]);
          peras-agda = pkgs.agdaPackages.mkDerivation {
            pname = "peras-agda";
            version = "0.1";
            meta = { };
            src = ./.;
            preConfigure = ''
              echo "open import README" > Everything.agda
            '';
            buildInputs = [ localAgda ];
          };
        in
        {
          packages.default = peras-agda;
          defaultPackage = peras-agda;
          devShell = pkgs.mkShell {
            buildInputs = [
              pkgs.nixpkgs-fmt
              localAgda
              localEmacs
              pkgs.mononoki
            ];
          };
        }
      );

  nixConfig = {
    bash-prompt = "\\n\\[\\033[1;32m\\][peras-agda:\\w]\\$\\[\\033[0m\\] ";
  };
}
