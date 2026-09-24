id: unixlike/desktop-not-wsl
statement: A graphical program reaches only a graphical home, and WSL outputs contain no Linux GUI program or graphical-session integration.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: fixture unixlike/tool/checks/flake-test

The WSL homes render inside a terminal the Windows domain declares. WSL GUI
support is outside the intended outputs, not a deferred feature. A proposal
to add it must first revise this invariant and its architecture rationale.
The class map in the composition file keeps `homeManager.desktop` out of both
WSL homes; the fixture evaluates both for graphical marker packages and the
Darwin home to prove the probe sees them where they belong. The NixOS-WSL
fixture also checks that Windows graphics-driver integration and graphical
Start Menu launchers remain disabled.
