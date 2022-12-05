{ lib
, python
, poetry2nix
}:

poetry2nix.mkPoetryApplication {
  inherit python;

  projectDir = ./.;
  pyproject = ./pyproject.toml;
  poetrylock = ./poetry.lock;

  pythonImportsCheck = [ "yretain" ];

  meta = with lib; {
    homepage = "https://yretain.com";
    description = "Why retain a customer product";
  };
}
