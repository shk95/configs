_: {
  modules.homeManager.darwin = {pkgs, ...}: {
    programs = {
      alacritty = {
        enable = true;
        package = pkgs.alacritty;
        settings = {
          cursor = {
            style = "Block";
          };

          window = {
            opacity = 0.9;
            dynamic_title = true;
            option_as_alt = "Both"; # Option key acts as Alt on macOS

            padding = {
              x = 24;
              y = 24;
            };
          };

          scrolling = {
            history = 10000;
          };

          font = {
            normal = {
              family = "JetBrainsMono Nerd Font Mono";
              style = "Regular";
            };
            bold = {
              family = "JetBrainsMono Nerd Font Mono";
            };
            bold_italic = {
              family = "JetBrainsMono Nerd Font Mono";
            };
            italic = {
              family = "JetBrainsMono Nerd Font Mono";
            };
            size = 14;
          };

          colors = {
            primary = {
              background = "0x1f2528";
              foreground = "0xc0c5ce";
            };

            normal = {
              black = "0x1f2528";
              red = "0xec5f67";
              green = "0x99c794";
              yellow = "0xfac863";
              blue = "0x6699cc";
              magenta = "0xc594c5";
              cyan = "0x5fb3b3";
              white = "0xc0c5ce";
            };

            bright = {
              black = "0x65737e";
              red = "0xec5f67";
              green = "0x99c794";
              yellow = "0xfac863";
              blue = "0x6699cc";
              magenta = "0xc594c5";
              cyan = "0x5fb3b3";
              white = "0xd8dee9";
            };
          };

          # Fix for shell path when launching from desktop
          # When launching from desktop, $SHELL may point to /bin/zsh instead of
          # the Nix-managed shell, causing environment issues
          #
          # -> try using `chsh` instead of this.
          #
          # terminal.shell = {
          #   program = "${pkgs.zsh}/bin/zsh";
          # };
        };
      };
    };
  };
}
