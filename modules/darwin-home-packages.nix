_: {
  modules.homeManager.darwin = {pkgs, ...}: {
    home.packages = with pkgs; [
      file
      gawk
      ghostscript
      gitflow
      glow
      gnused
      gnutar
      monolith
      pup
      R
      yq-go
      uv
    ];
  };
}
