$ErrorActionPreference = "Stop"

if (-not (Get-Command rustup -ErrorAction SilentlyContinue)) {
  Invoke-WebRequest -Uri https://win.rustup.rs -OutFile rustup-init.exe
  .\rustup-init.exe -y --default-toolchain stable
}

$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"

$target = ""
$tag = ""
$build = $env:CIBW_BUILD
if ($build -like "*manylinux_x86_64*" -or $build -like "*linux_x86_64*" -or $build -like "*musllinux_x86_64*") {
  $target = "x86_64-unknown-linux-gnu"
  $tag = "linux-x86_64"
} elseif ($build -like "*manylinux_aarch64*" -or $build -like "*linux_aarch64*" -or $build -like "*musllinux_aarch64*") {
  $target = "aarch64-unknown-linux-gnu"
  $tag = "linux-aarch64"
} elseif ($build -like "*win_amd64*") {
  $target = "x86_64-pc-windows-msvc"
  $tag = "windows-x86_64"
}

if ($target) {
  rustup target add $target
  $env:CARGO_BUILD_TARGET = $target
  $env:GHLANG_PLATFORM_TAG = $tag
  cargo build --manifest-path tokount\Cargo.toml --release --target $target
} else {
  cargo build --manifest-path tokount\Cargo.toml --release
}
python .github\workflows\scripts\copy_tokount_binary.py
