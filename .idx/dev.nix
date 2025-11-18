{ pkgs, ... }: {
  # Channel specifies the Nix package set to use.
  channel = "stable-23.11"; # This is the default.

  # Use `pkgs` to declare Nix packages to install.
  # For example, `pkgs.nodePackages.typescript-language-server`.
  packages = [
    pkgs.python3
    pkgs.bashInteractive
  ];

  # The `idx` section contains configuration that is specific to
  # Project IDX.
  idx = {
    # Use the `workspace` section to configure your workspace environment.
    workspace = {
      # Use `onCreate` to run commands when your workspace is created.
      onCreate = {
        # Example: install dependencies from a requirements.txt file.
        install-deps = "pip install -r requirements.txt";
      };
      # Use `onStart` to run commands when your workspace starts.
      onStart = {
        # Example: start a background development server.
        # start-dev-server = "npm run dev";
      };
    };
  };

  # Use the `previews` section to configure application previews.
  previews = {
    enable = true;
    previews = {
      # The `web` preview is a special preview that comes with a
      # web server and a browser that you can use to preview your
      # application.
      web = {
        command = ["python", "-u", "app.py"];
        manager = "web";
      };
    };
  };
}
