{
  # tool/checks/eval-coverage-test: a flavour the flake exports but that
  # lists nothing. tool/checks/test must fail rather than pass on an empty
  # report.
  description = "eval-coverage fixture: an exported flavour with no configuration";
  outputs = _: {
    homeConfigurations = {};
  };
}
