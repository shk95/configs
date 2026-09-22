# Niri owns the graphical session and the portal implementation selected by
# nixpkgs' NixOS module. greetd provides a small display manager without
# importing a desktop environment.
_: {
  modules.nixos.graphical = {pkgs, ...}: {
    programs = {
      niri = {
        enable = true;
        useNautilus = false;
      };
      thunar.enable = true;
    };

    services.greetd = {
      enable = true;
      settings.default_session.command = "${pkgs.tuigreet}/bin/tuigreet --time --remember --remember-user-session --cmd niri-session";
    };
  };
}
