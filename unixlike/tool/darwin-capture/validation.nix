# Pure JSON document validation for the two capture units. No evaluator subprocess.
{contract, ...}: let
  fail = message: throw "Darwin capture: ${message}";
  # fromJSON checks syntax, but accepts duplicate keys. Scan its original bytes
  # separately, decoding object keys before comparing them within each object.
  strictJSON = text: let
    size = builtins.stringLength text;
    char = i: builtins.substring i 1 text;
    ws = c: builtins.elem c [" " "\n" "\r" "\t"];
    stringEnd = i: escaped:
      if i >= size
      then fail "unterminated JSON string"
      else if escaped
      then stringEnd (i + 1) false
      else if char i == "\\"
      then stringEnd (i + 1) true
      else if char i == "\""
      then i + 1
      else stringEnd (i + 1) false;
    atomEnd = i:
      if i >= size || ws (char i) || builtins.elem (char i) ["," "]" "}" ":"]
      then i
      else atomEnd (i + 1);
    scan = i: stack:
      if i >= size
      then true
      else let
        c = char i;
        head =
          if stack == []
          then null
          else builtins.head stack;
        rest =
          if stack == []
          then []
          else builtins.tail stack;
      in
        if ws c
        then scan (i + 1) stack
        else if c == "{"
        then
          scan (i + 1) ([
              {
                object = true;
                key = true;
                names = [];
              }
            ]
            ++ stack)
        else if c == "["
        then scan (i + 1) ([{object = false;}] ++ stack)
        else if c == "}" || c == "]"
        then scan (i + 1) rest
        else if c == "," && head != null && head.object
        then scan (i + 1) ([(head // {key = true;})] ++ rest)
        else if c == ":" && head != null && head.object
        then scan (i + 1) ([(head // {key = false;})] ++ rest)
        else if c == "," || c == ":"
        then scan (i + 1) stack
        else if c == "\""
        then let
          end = stringEnd (i + 1) false;
          decoded = builtins.fromJSON (builtins.substring i (end - i) text);
          isKey = head != null && head.object && head.key;
        in
          if isKey && builtins.elem decoded head.names
          then fail "duplicate JSON object key"
          else
            scan end (
              if isKey
              then [(head // {names = head.names ++ [decoded];})] ++ rest
              else stack
            )
        else let
          end = atomEnd (i + 1);
          token = builtins.substring i (end - i) text;
          integer = builtins.match "-?[0-9]+" token != null;
        in
          # fromJSON otherwise silently converts negative integer overflow to
          # float. Fractions/exponents keep their explicit floating semantics.
          if integer && !builtins.isInt (builtins.fromJSON token)
          then fail "JSON integer outside Nix signed 64-bit range"
          else scan end stack;
    parsed = builtins.fromJSON text;
  in
    builtins.deepSeq parsed (builtins.seq (scan 0 []) parsed);
  exact = names: value: builtins.isAttrs value && builtins.attrNames value == builtins.sort builtins.lessThan names;
  inherit (builtins) all;
  validSettings = unit: settings: let
    u = contract.units.${unit};
  in
    if unit == "karabiner"
    then
      exact u.parents settings
      && builtins.isAttrs settings.global
      && all (key: !(builtins.hasAttr key settings.global)) u.obsoleteGlobalKeys
      && all (key: !(builtins.hasAttr key settings.global) || builtins.isBool settings.global.${key}) u.globalBooleanKeys
      && builtins.isList settings.profiles
      && builtins.length settings.profiles >= u.profilesMinimum
      && all (key: settings.${key} != {}) u.requiredNonemptyObjects
      && all (profile:
        builtins.isAttrs profile
        && profile != {}
        && all (key: !(builtins.hasAttr key profile) || builtins.isString profile.${key}) u.profileStringKeys
        && all (key: !(builtins.hasAttr key profile) || builtins.isBool profile.${key}) u.profileBooleanKeys
        && all (key: !(builtins.hasAttr key profile) || builtins.isList profile.${key}) u.profileArrayKeys
        && all (key: !(builtins.hasAttr key profile) || builtins.isAttrs profile.${key}) u.profileObjectKeys
        && all (key: !(builtins.hasAttr key profile) || (profile.${key} != {} && profile.${key} != [])) u.unstableEmptyProfileKeys
        && (!(profile ? complex_modifications.rules)
          || (builtins.isList profile.complex_modifications.rules
            && builtins.length profile.complex_modifications.rules >= u.complexRulesMinimum
            && all builtins.isAttrs profile.complex_modifications.rules)))
      settings.profiles
    else
      exact [u.parent] settings
      && exact u.entries settings.${u.parent}
      && all (entry: let
        e = settings.${u.parent}.${entry};
      in
        exact u.entryKeys e
        && builtins.isBool e.enabled
        && exact u.valueKeys e.value
        && e.value.type == u.valueType
        && builtins.isList e.value.parameters
        && builtins.length e.value.parameters == u.parameterCount
        && all (n: builtins.isInt n && n >= u.parameterMinimum && n <= u.parameterMaximum) e.value.parameters)
      u.entries;
  document = unit: path: let
    d = strictJSON (builtins.readFile path);
  in
    if
      !(exact ["formatVersion" "source" "settings"] d)
      || !(builtins.isInt d.formatVersion && d.formatVersion == contract.formatVersion)
      || !(builtins.elem d.source ["host" "configs"])
      || !(builtins.isAttrs d.settings)
      || (d.source == "host" && !(validSettings unit d.settings))
    then fail "invalid ${unit} settings document"
    else d;
in {inherit strictJSON validSettings document;}
