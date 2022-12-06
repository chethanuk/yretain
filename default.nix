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
    description = "This project was generated with fastapi-mvc.";
  };
}
