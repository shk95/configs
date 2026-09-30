# Public input and compatibility data, checked against the typed constructors.
{
  formatVersion = 1;
  domain = "unixlike";
  entryPoints = {
    mkNixos = {
      path = "lib.mkNixos";
      inputs = {
        system = {
          type = "enum";
          required = true;
        };
        user = {
          type = "string";
          required = true;
        };
        git = {
          type = "nameEmail";
          required = true;
        };
        environment = {
          type = "selection";
          required = false;
          defaults = {
            wsl = false;
            graphicalWhenWsl = false;
            graphicalOtherwise = true;
          };
        };
        systemModules = {
          type = "moduleList";
          required = false;
        };
        homeModules = {
          type = "moduleList";
          required = false;
        };
      };
      output = "nixosConfigurations.<name>.config.system.build.toplevel";
    };
    mkDarwin = {
      path = "lib.mkDarwin";
      inputs = {
        system = {
          type = "enum";
          required = true;
        };
        user = {
          type = "string";
          required = true;
        };
        git = {
          type = "nameEmail";
          required = true;
        };
        environment = {
          type = "selection";
          required = false;
          defaults = {
            wsl = false;
            graphical = true;
          };
        };
        systemModules = {
          type = "moduleList";
          required = false;
        };
        homeModules = {
          type = "moduleList";
          required = false;
        };
      };
      output = "darwinConfigurations.<name>.config.system.build.toplevel";
    };
    mkHome = {
      path = "lib.mkHome";
      inputs = {
        system = {
          type = "enum";
          required = true;
        };
        user = {
          type = "string";
          required = true;
        };
        homeDirectory = {
          type = "absolutePathString";
          required = true;
        };
        git = {
          type = "nameEmail";
          required = true;
        };
        environment = {
          type = "selection";
          required = false;
          defaults = {
            wsl = false;
            graphicalWhenWsl = false;
            graphicalOtherwise = true;
          };
        };
        homeModules = {
          type = "moduleList";
          required = false;
        };
      };
      output = "homeConfigurations.<name>.activationPackage";
    };
  };
  constraints = {
    mkNixos = {
      systems = ["x86_64-linux" "aarch64-linux"];
      graphicalWithWsl = false;
      wslRequiresHostIntegration = true;
    };
    mkDarwin = {
      systems = ["aarch64-darwin"];
      wsl = false;
    };
    mkHome = {
      systems = ["x86_64-linux"];
      graphicalWithWsl = false;
      systemModules = false;
    };
  };
  compatibilityDefaults = {
    nixos = "25.11";
    homeManager = "25.11";
    nixDarwin = 6;
  };
  changes = [
    {
      id = "mkHome-explicit-home-directory";
      entryPoint = "mkHome";
      before = "mkHome omitted homeDirectory and derived /home/<user>";
      after = "mkHome requires homeDirectory";
      guidance = "Pass the actual home directory; keep any existing home.stateVersion override in homeModules.";
    }
    {
      id = "mkHome-explicit-environment";
      entryPoint = "mkHome";
      before = "mkHome always selected WSL CLI composition";
      after = "mkHome selects WSL and graphics through environment";
      guidance = "Set environment.wsl = true for an existing WSL home; explicitly set graphical = false for a general CLI home.";
    }
    {
      id = "mkNixos-environment-and-host-modules";
      entryPoint = "mkNixos";
      before = "mkNixos required name, host.kind, host.stateVersion and profiles";
      after = "mkNixos selects environment from system, user and environment; host modules realize the machine";
      guidance = "Move hostname, account, machine, access and storage settings into systemModules; retain effective stateVersion explicitly where it differs from the provider default. Pass the output name in the consumer flake.";
    }
    {
      id = "mkDarwin-host-realization";
      entryPoint = "mkDarwin";
      before = "mkDarwin required host.system, host.hostName and host.user";
      after = "mkDarwin receives system and user while systemModules own hostname, account, daemon and app selection";
      guidance = "Move hostname and account settings to systemModules and retain any effective compatibility value that differs from the provider default.";
    }
  ];
}
