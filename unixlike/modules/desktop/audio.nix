# Audio for a graphical NixOS session. PipeWire owns the PulseAudio and ALSA
# compatibility layers; no second sound server is enabled beside it.
_: {
  modules.nixos.graphical = {
    security.rtkit.enable = true;

    services.pipewire = {
      enable = true;
      alsa.enable = true;
      alsa.support32Bit = true;
      pulse.enable = true;
      wireplumber.enable = true;
    };
  };
}
