param(
    [string]$MobileSource = "PKHeXMAUI",
    [string]$CoreSource = "ExpansionCore"
)

$ErrorActionPreference = "Stop"
$projectPath = Join-Path $MobileSource "PKHeX.MAUI.csproj"
$coreProject = Join-Path $CoreSource "PKHeX.Core/PKHeX.Core.csproj"
if (-not (Test-Path $projectPath)) { throw "PKHeX.MAUI.csproj missing: $projectPath" }
if (-not (Test-Path $coreProject)) { throw "Aqua-0 v1.0 PKHeX.Core.csproj missing: $coreProject" }

$text = Get-Content -LiteralPath $projectPath -Raw -Encoding UTF8
$nuget = '<PackageReference Include="PKHeX.Core" Version="26.7.7" />'
$projectReference = '<ProjectReference Include="..\ExpansionCore\PKHeX.Core\PKHeX.Core.csproj" />'

if ($text.Contains($nuget)) {
    $text = $text.Replace($nuget, $projectReference)
} elseif (-not $text.Contains($projectReference)) {
    throw "Unexpected upstream PKHeX.Core dependency. Review the upstream changes before building."
}

# Preserve all original XAML screens, Box/Party, editor tabs, utilities and
# bundled species/form/shiny sprites from santacrab2/PKHeXMAUI.
# Use a different Android ID so this fork can coexist with the official app.
if (-not $text.Contains("<ApplicationId>org.pkhex.gen7expansion.maui</ApplicationId>")) {
    $properties = @'
  <PropertyGroup>
    <ApplicationTitle>PKHeX Gen7 Expansion</ApplicationTitle>
    <ApplicationId>org.pkhex.gen7expansion.maui</ApplicationId>
    <ApplicationDisplayVersion>0.8.0</ApplicationDisplayVersion>
    <ApplicationVersion>8</ApplicationVersion>
    <EmbedAssembliesIntoApk>true</EmbedAssembliesIntoApk>
    <AndroidUseSharedRuntime>false</AndroidUseSharedRuntime>
    <AndroidPackageFormats>apk</AndroidPackageFormats>
    <RunAOTCompilation>false</RunAOTCompilation>
  </PropertyGroup>
'@
    $text = $text.Replace("</Project>", $properties + [Environment]::NewLine + "</Project>")
}

Set-Content -LiteralPath $projectPath -Value $text -Encoding UTF8
Write-Host "Using full santacrab2 PKHeX.MAUI UI with Aqua-0 PKHeX.Core Expansion v1.0"
Write-Host "The original species, form, item and shiny sprite resources remain bundled."
python (Join-Path $PSScriptRoot "patch-pkhax-updates.py") --root $MobileSource
if ($LASTEXITCODE -ne 0) { throw "PKHaX and update-suppression patch failed" }
python (Join-Path $PSScriptRoot "patch-expansion-v07.py") --root $MobileSource
if ($LASTEXITCODE -ne 0) { throw "Expansion v0.7 Safe Save/sprites/diagnostics patches failed" }
python (Join-Path $PSScriptRoot "patch-save-hotfix-v08.py") --root $MobileSource
if ($LASTEXITCODE -ne 0) { throw "v0.8 save signature/inventory hotfix patches failed" }


