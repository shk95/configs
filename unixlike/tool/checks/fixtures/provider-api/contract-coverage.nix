# INV unixlike/typed-identity: the finite published input contract accepts its
# declared values and refuses omitted required fields and wrong native types.
{provider}: let
  lib = provider.inputs.nixpkgs.lib;
  contract = builtins.fromJSON (builtins.readFile (provider.outPath + "/api/contract.json"));
  base = name:
    {
      system = builtins.head contract.constraints.${name}.systems;
      user = "example";
      git = {
        name = "Example";
        email = "example@example.invalid";
      };
    }
    // lib.optionalAttrs (name == "mkHome") {homeDirectory = "/home/" + "example";};
  validValue = name: type:
    {
      string = "example";
      nameEmail = {
        name = "Example";
        email = "example@example.invalid";
      };
      enum = (base name).system;
      selection = {
        wsl = false;
        graphical = false;
      };
      moduleList = [];
      absolutePathString = "/home/" + "example";
    }.${
      type
    };
  invalidValue = type:
    {
      string = 42;
      nameEmail = {
        name = "Example";
        email = 42;
      };
      enum = "unsupported-system";
      selection = {wsl = "yes";};
      moduleList = "not-a-list";
      absolutePathString = "relative";
    }.${
      type
    };
  constructor = name: lib.attrByPath (lib.splitString "." contract.entryPoints.${name}.path) null provider;
  config = name: inputs: (constructor name inputs).config;
  probe = name: inputs:
    if name == "mkHome"
    then (config name inputs).home.stateVersion
    else (config name inputs).system.stateVersion;
  succeeds = value: (builtins.tryEval (builtins.deepSeq value true)).success;
  check = name: result: {inherit name result;};
  fields = name:
    lib.concatMap (field: let
      description = contract.entryPoints.${name}.inputs.${field};
    in
      [
        (check "${name}.${field}: declared ${description.type}" (succeeds (probe name ((base name) // {${field} = validValue name description.type;}))))
        (check "${name}.${field}: wrong ${description.type}" (!(succeeds (probe name ((base name) // {${field} = invalidValue description.type;})))))
      ]
      ++ lib.optional description.required (check "${name}.${field}: required" (!(succeeds (probe name (builtins.removeAttrs (base name) [field]))))))
    (builtins.attrNames contract.entryPoints.${name}.inputs);
  systems = name:
    map (system: check "${name}: supported ${system}" (succeeds (probe name ((base name) // {inherit system;})))) contract.constraints.${name}.systems;
  graphical = name: inputs: let
    result = config name inputs;
    home =
      if name == "mkHome"
      then result
      else result.home-manager.users.example;
  in
    builtins.elem "wezterm" (map lib.getName home.home.packages);
  defaults = name: let
    d = contract.entryPoints.${name}.inputs.environment.defaults;
    constraints = contract.constraints.${name};
    wslAllowed = constraints.wsl or true;
    graphicalWslAllowed = wslAllowed && (constraints.graphicalWithWsl or true);
    expectedOutputs = {
      mkNixos = "nixosConfigurations.<name>.config.system.build.toplevel";
      mkDarwin = "darwinConfigurations.<name>.config.system.build.toplevel";
      mkHome = "homeConfigurations.<name>.activationPackage";
    };
    expected =
      d.graphical or (
        if d.wsl
        then d.graphicalWhenWsl
        else d.graphicalOtherwise
      );
  in [
    (check "${name}: output selector" (contract.entryPoints.${name}.output == expectedOutputs.${name}))
    (check "${name}: omitted environment defaults" (graphical name (base name) == expected))
    (check "${name}: empty environment defaults" (graphical name ((base name) // {environment = {};}) == expected))
    (check "${name}: empty homeModules neutral" (probe name ((base name) // {homeModules = [];}) == probe name (base name)))
    (check "${name}: unknown field refused" (!(succeeds (probe name ((base name) // {unknownField = true;})))))
    (check "${name}: WSL selection constraint" (succeeds (probe name ((base name)
      // {
        environment = {
          wsl = true;
          graphical = false;
        };
      }))
    == wslAllowed))
    (check "${name}: graphical WSL constraint" (succeeds (probe name ((base name)
      // {
        environment = {
          wsl = true;
          graphical = true;
        };
      }))
    == graphicalWslAllowed))
  ];
  cases = lib.concatMap (name: fields name ++ systems name ++ defaults name) (builtins.attrNames contract.entryPoints);
in {
  count = builtins.length cases;
  failures = map (case: case.name) (builtins.filter (case: !case.result) cases);
}
