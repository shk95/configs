id: unixlike/composition-in-one-place
statement: Only one file decides which module classes reach a Unix-like host; a feature module contributes to classes and never names a host or forces another class's decision.
rationale: AGENTS.md § Goal and authority
enforced-by: pending #127
owner: repository maintainer

The classes are the whole interface between a feature file and a host. The
known leak is `modules/zellij.nix`, where the desktop class forces a file the
shared class already declares, so a feature file decides class precedence
instead of the composition file deciding what each class contains. No check
refuses that today; #127 owns one.
