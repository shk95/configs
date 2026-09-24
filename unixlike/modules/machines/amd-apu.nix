# The portable graphics and CPU side of the physical AMD APU desktop. Mesa is
# supplied by hardware.graphics from the shared graphical class and provides
# the AMD Vulkan and VA-API implementations; no vendor package or driver
# override is needed.
_: {
  modules.nixos.desktop = {config, ...}: {
    hardware = {
      amdgpu.initrd.enable = true;
      cpu.amd.updateMicrocode = true;
      enableRedistributableFirmware = true;
      graphics.enable32Bit = true;
    };

    # INV unixlike/amd-apu-desktop-portable-base
    assertions = [
      {
        assertion =
          config.hardware.amdgpu.initrd.enable
          && builtins.elem "amdgpu" config.boot.initrd.kernelModules
          && config.hardware.cpu.amd.updateMicrocode
          && config.hardware.enableRedistributableFirmware
          && config.hardware.graphics.enable
          && config.hardware.graphics.enable32Bit
          && (config.hardware.graphics.package.pname or "") == "mesa";
        message = "INV unixlike/amd-apu-desktop-portable-base: the physical desktop must retain the distribution AMDGPU and Mesa path";
      }
    ];
  };
}
