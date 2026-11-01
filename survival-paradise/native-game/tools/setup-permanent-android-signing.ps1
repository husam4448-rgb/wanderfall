# One-time local stable signing setup for Survival Paradise Android builds.
# Requires Java keytool and authenticated GitHub CLI (gh auth login).
# Never commit your .jks or upload it to a public release.
param([string]$Repository = "husam4448-rgb/wanderfall")
$ErrorActionPreference = "Stop"
$folder = Join-Path $env:USERPROFILE "SurvivalParadiseSigning"
New-Item -ItemType Directory -Path $folder -Force | Out-Null
$store = Join-Path $folder "survivalparadise-permanent.jks"
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  throw "GitHub CLI (gh) is required. Install GitHub CLI and run gh auth login."
}
if (-not (Get-Command keytool -ErrorAction SilentlyContinue)) {
  throw "Java JDK keytool is required. Install JDK 17 or later."
}
if (-not (Test-Path $store)) {
  Write-Host "Creating private signing key in your user directory."
  & keytool -genkeypair -v -keystore $store -alias survivalparadise -keyalg RSA -keysize 3072 -validity 10000 -dname "CN=Survival Paradise,OU=Development,O=Survival Paradise"
  if ($LASTEXITCODE -ne 0) { throw "keytool failed." }
} else {
  Write-Host "Reusing existing keystore; never replace an active signing key."
}
$secure = Read-Host "Enter keystore password (not stored in script)" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
  $password = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
  if ([string]::IsNullOrWhiteSpace($password)) { throw "Empty password." }
  $b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($store))
  $b64 | gh secret set SP_SIGNING_KEYSTORE_BASE64 -R $Repository
  if ($LASTEXITCODE -ne 0) { throw "Could not upload keystore secret." }
  $password | gh secret set SP_SIGNING_PASSWORD -R $Repository
  if ($LASTEXITCODE -ne 0) { throw "Could not upload password secret." }
  $password | gh secret set SP_SIGNING_KEY_PASSWORD -R $Repository
  if ($LASTEXITCODE -ne 0) { throw "Could not upload key password secret." }
  "survivalparadise" | gh secret set SP_SIGNING_ALIAS -R $Repository
  if ($LASTEXITCODE -ne 0) { throw "Could not upload alias secret." }
} finally {
  if ($ptr -ne [IntPtr]::Zero) {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
  }
  $password = $null
}
Write-Host "Signing secrets configured. Back up $store securely, including its password."
Write-Host "For update compatibility, all future APKs must be signed with THIS SAME key."
Write-Host "Existing debug-signed APKs cannot be upgraded in place to this new key."
