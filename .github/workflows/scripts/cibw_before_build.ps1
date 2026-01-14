$ErrorActionPreference = "Stop"

if (-not (Get-Command rustup -ErrorAction SilentlyContinue)) {
  Invoke-WebRequest -Uri https://win.rustup.rs -OutFile rustup-init.exe
  .\rustup-init.exe -y --default-toolchain stable
}

$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"

cargo build --manifest-path tokount\Cargo.toml --release
python .github\workflows\scripts\copy_tokount_binary.py
