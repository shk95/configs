_: {
  modules.homeManager.shared = {
    # `programs.btop` contributes its own package, so INV
    # unixlike/package-ownership keeps btop out of modules/foundation/packages.nix — the
    # same shape modules/programs/bat.nix and modules/programs/lazygit.nix use for their
    # packages (docs/policy/decisions/unixlike/package-ownership-by-generating-module.md).
    #
    # btop uses a truecolour theme rather than the terminal ANSI palette.
    # Keep its light UI and accents aligned with Bluegray Light. With
    # theme_background=false the terminal still owns the page background.
    # Reserve ochre for elevated temperature; ordinary graphs stay cool.
    programs.btop = {
      enable = true;
      settings = {
        color_theme = "bluegray-light";
        theme_background = false;
        truecolor = true;
        vim_keys = true;
        rounded_corners = true;
        graph_symbol = "braille";
        update_ms = 2000;
        proc_sorting = "cpu lazy";
        shown_boxes = "cpu mem net proc";
      };
      themes.bluegray-light = ''
        theme[main_bg]="#ECEFF3"
        theme[main_fg]="#303640"
        theme[title]="#303640"
        theme[hi_fg]="#355A87"
        theme[selected_bg]="#D6E1F0"
        theme[selected_fg]="#303640"
        theme[inactive_fg]="#576474"
        theme[graph_text]="#576474"
        theme[meter_bg]="#E1E6ED"
        theme[proc_misc]="#35604A"
        theme[cpu_box]="#355A87"
        theme[mem_box]="#35604A"
        theme[net_box]="#664C82"
        theme[proc_box]="#2D626D"
        theme[div_line]="#576474"
        theme[temp_start]="#355A87"
        theme[temp_mid]="#76561F"
        theme[temp_end]="#9A3F4A"
        theme[cpu_start]="#2D626D"
        theme[cpu_mid]="#355A87"
        theme[cpu_end]="#9A3F4A"
        theme[free_start]="#E1E6ED"
        theme[free_mid]="#576474"
        theme[free_end]="#35604A"
        theme[cached_start]="#576474"
        theme[cached_mid]="#355A87"
        theme[cached_end]="#2D626D"
        theme[available_start]="#355A87"
        theme[available_mid]="#2D626D"
        theme[available_end]="#35604A"
        theme[used_start]="#35604A"
        theme[used_mid]="#664C82"
        theme[used_end]="#9A3F4A"
        theme[download_start]="#576474"
        theme[download_mid]="#355A87"
        theme[download_end]="#2D626D"
        theme[upload_start]="#576474"
        theme[upload_mid]="#664C82"
        theme[upload_end]="#355A87"
        theme[process_start]="#35604A"
        theme[process_mid]="#355A87"
        theme[process_end]="#9A3F4A"
        theme[proc_pause_bg]="#9A3F4A"
        theme[proc_follow_bg]="#355A87"
        theme[proc_banner_bg]="#664C82"
        theme[proc_banner_fg]="#ECEFF3"
        theme[followed_bg]="#355A87"
        theme[followed_fg]="#ECEFF3"
      '';
    };
  };
}
