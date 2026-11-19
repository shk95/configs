_: {
  programCatalog.yt-dlp = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "yt-dlp";
      packageOnly = true;
    };
  };
}
