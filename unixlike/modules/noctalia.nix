# Declarative Noctalia baseline. Runtime UI changes remain in Noctalia's state
# layer; personal wallpaper, avatar, weather and location state are absent.
_: {
  modules.homeManager.linuxGraphical.programs.noctalia = {
    enable = true;
    systemd.enable = false;
    checkConfig = true;
    settings = {
      accessibility.ui_scale = 1.0;

      shell = {
        setup_wizard_enabled = false;
        screenshot = {
          annotate = true;
          directory = "~/Pictures/Screenshots";
        };
      };

      osd.position = "top_right";

      theme = {
        source = "builtin";
        builtin = "Catppuccin";
        mode = "light";
        templates = {
          enable_builtin_templates = false;
          enable_community_templates = false;
        };
      };

      bar.main = {
        background_opacity = 0.85;
        margin_ends = 16;
        start = [
          "launcher"
          "workspaces"
          "cpu"
          "ram"
          "net_rx"
          "net_tx"
        ];
      };

      widget = {
        clock = {
          type = "clock";
          format = "{:%Y-%m-%d %A %H:%M}";
        };
        media.hide_when_no_media = true;
        cpu = {
          type = "sysmon";
          stat = "cpu_usage";
        };
        ram = {
          type = "sysmon";
          stat = "ram_pct";
        };
        net_rx = {
          type = "sysmon";
          stat = "net_rx";
          network_speed_compact = true;
        };
        net_tx = {
          type = "sysmon";
          stat = "net_tx";
          network_speed_compact = true;
        };
        network.show_label = false;
      };
    };
  };
}
