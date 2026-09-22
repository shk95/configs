# Niri interaction model adapted from Ryan Yin's MIT-licensed configuration at
# 3b13291216bbea04169360b9d8a18a210d816c04. The KDL is rewritten for this
# repository's applications and contains no host, monitor or personal path.
_: {
  modules.homeManager.linuxGraphical = {pkgs, ...}: let
    rawConfig = pkgs.writeText "niri-config.kdl" ''
      input {
          keyboard {
              xkb {}
          }
          touchpad {
              tap
              dwt
              natural-scroll
          }
      }

      layout {
          gaps 8
          center-focused-column "on-overflow"
          preset-column-widths {
              proportion 0.333333
              proportion 0.5
              proportion 0.666667
          }
          default-column-width { proportion 0.5; }
          focus-ring {
              width 3
              active-color "#268bd2"
              inactive-color "#93a1a1"
          }
          border { off; }
      }

      prefer-no-csd
      screenshot-path "~/Pictures/Screenshots/Screenshot from %Y-%m-%d %H-%M-%S.png"
      hotkey-overlay { skip-at-startup; }

      spawn-at-startup "noctalia"

      binds {
          Mod+Return { spawn "ghostty"; }
          Mod+Shift+Return { spawn "wezterm"; }
          Mod+D { spawn "noctalia" "msg" "panel-toggle" "launcher"; }
          Mod+S { spawn "noctalia" "msg" "panel-toggle" "control-center"; }
          Mod+Shift+V { spawn "noctalia" "msg" "panel-toggle" "clipboard"; }
          Ctrl+Alt+L { spawn "noctalia" "msg" "session" "lock"; }

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

          Mod+H { focus-column-left; }
          Mod+J { focus-window-down; }
          Mod+K { focus-window-up; }
          Mod+L { focus-column-right; }
          Mod+Ctrl+H { move-column-left; }
          Mod+Ctrl+J { move-window-down; }
          Mod+Ctrl+K { move-window-up; }
          Mod+Ctrl+L { move-column-right; }
          Mod+U { focus-workspace-down; }
          Mod+I { focus-workspace-up; }
          Mod+Ctrl+U { move-column-to-workspace-down; }
          Mod+Ctrl+I { move-column-to-workspace-up; }
          Mod+R { switch-preset-column-width; }
          Mod+Shift+R { switch-preset-window-height; }
          Mod+F { maximize-column; }
          Mod+Shift+F { fullscreen-window; }
          Mod+V { toggle-window-floating; }
          Mod+W { toggle-column-tabbed-display; }
          Mod+Minus { set-column-width "-10%"; }
          Mod+Equal { set-column-width "+10%"; }
          Mod+Escape allow-inhibiting=false { toggle-keyboard-shortcuts-inhibit; }
          Mod+Q repeat=false { close-window; }
          Ctrl+Alt+Delete { quit; }

          Print { spawn "noctalia" "msg" "screenshot-region"; }
          Ctrl+Print { spawn "noctalia" "msg" "screenshot-fullscreen"; }
          Mod+Shift+P { power-off-monitors; }
      }

      window-rule {
          match app-id="com.mitchellh.ghostty"
          open-on-workspace "terminal"
          open-maximized true
      }
      window-rule {
          match app-id="org.wezfurlong.wezterm"
          open-on-workspace "terminal"
          open-maximized true
      }
      window-rule {
          match app-id="firefox"
          open-on-workspace "browser"
          open-maximized true
      }
      window-rule {
          match app-id="thunar"
          open-on-workspace "utility"
      }
      window-rule {
          match app-id="^mpv$"
          open-on-workspace "media"
      }

      debug { honor-xdg-activation-with-invalid-serial; }
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
    home.packages = [pkgs.xwayland-satellite];
    xdg.configFile."niri/config.kdl".source = validatedConfig;
  };
}
