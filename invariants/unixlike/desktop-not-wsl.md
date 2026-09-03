id: unixlike/desktop-not-wsl
statement: A graphical program reaches only a home whose class is graphical, and the WSL homes receive none.
rationale: docs/architecture.md § Unix-like domain
enforced-by: fixture tool/checks/flake-test

The WSL homes render inside a terminal the Windows domain declares, so a
graphical program there is either dead weight or a second authority over the
same screen. The class map in the composition file is the only thing that
keeps `homeManager.desktop` out of them; the fixture evaluates both WSL homes
for the desktop marker package and the Darwin home to prove the probe sees it
where it belongs.
