# Validate the reusable Niri session configuration. Consumers can supply their own source.
_: {
  modules.homeManager.linuxGraphical = {
    config,
    lib,
    pkgs,
    ...
  }: let
    rawConfig = pkgs.writeText "niri-config.kdl" ''
      ${lib.optionalString (config.configs.niri.repeatDelayMs != null) ''
        input {
            keyboard {
                repeat-delay ${toString config.configs.niri.repeatDelayMs}
            }
        }
      ''}
      spawn-at-startup "noctalia"
      binds {
          ${lib.optionalString config.xdg.terminal-exec.enable ''Mod+Return { spawn "xdg-terminal-exec"; }''}
          Ctrl+Alt+L { spawn "noctalia" "msg" "session" "lock"; }
          Mod+Escape allow-inhibiting=false { toggle-keyboard-shortcuts-inhibit; }

          XF86AudioRaiseVolume allow-when-locked=true { spawn "noctalia" "msg" "volume-up"; }
          XF86AudioLowerVolume allow-when-locked=true { spawn "noctalia" "msg" "volume-down"; }
          XF86AudioMute allow-when-locked=true { spawn "noctalia" "msg" "volume-mute"; }
          XF86AudioMicMute allow-when-locked=true { spawn "noctalia" "msg" "mic-mute"; }
          XF86AudioPlay allow-when-locked=true { spawn "noctalia" "msg" "media" "toggle"; }
          XF86AudioStop allow-when-locked=true { spawn "noctalia" "msg" "media" "pause"; }
          XF86AudioPrev allow-when-locked=true { spawn "noctalia" "msg" "media" "previous"; }
          XF86AudioNext allow-when-locked=true { spawn "noctalia" "msg" "media" "next"; }
          XF86MonBrightnessUp allow-when-locked=true { spawn "noctalia" "msg" "brightness-up"; }
          XF86MonBrightnessDown allow-when-locked=true { spawn "noctalia" "msg" "brightness-down"; }
      }
      layer-rule {
          match namespace="^noctalia-backdrop"
          place-within-backdrop true
      }
    '';

    validatedConfig =
      pkgs.runCommand "validated-niri-config.kdl" {
        nativeBuildInputs = [pkgs.niri];
      } ''
        niri validate -c ${rawConfig}
        cp ${rawConfig} "$out"
      '';
  in {
    options.configs.niri.repeatDelayMs = lib.mkOption {
      type = lib.types.nullOr lib.types.ints.positive;
      default = null;
      description = "Delay in milliseconds before Niri repeats a held key; null keeps Niri's default.";
    };

    config = {
      home.packages = [pkgs.xwayland-satellite];
      xdg.configFile."niri/config.kdl".source = lib.mkDefault validatedConfig;
    };
  };
}
