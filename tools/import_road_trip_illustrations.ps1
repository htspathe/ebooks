[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$LibraryZip,
    [Parameter(Mandatory = $true)][string]$ApprovedOnlyZip
)
$ErrorActionPreference = "Stop"
$ExpectedBranch = "kdp/road-trip-illustration-import-v1"
$BookPrefix = "books/road-trip-activity-6-10/"
$BookFolder = "books/road-trip-activity-6-10"

function Assert-CommandSuccess([string]$Message) {
    if ($LASTEXITCODE -ne 0) { throw "$Message (exit code $LASTEXITCODE)" }
}
function Get-ZipEntryHash($Archive, [string]$EntryName) {
    $entry = $Archive.GetEntry($EntryName)
    if ($null -eq $entry) { throw "Missing archive entry: $EntryName" }
    $stream = $entry.Open()
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha.ComputeHash($stream)
        return ([System.BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
    } finally {
        $stream.Dispose()
        $sha.Dispose()
    }
}
function Assert-SafeArchive($Archive, [string]$RequiredPrefix) {
    foreach ($entry in $Archive.Entries) {
        $name = $entry.FullName.Replace("\", "/")
        if ($name.StartsWith("/") -or $name -match '(^|/)\.\.(/|$)') { throw "Unsafe path in ZIP: $name" }
        if ($RequiredPrefix -and -not $name.StartsWith($RequiredPrefix, [System.StringComparison]::Ordinal)) {
            throw "Unexpected path outside $RequiredPrefix : $name"
        }
    }
}

$LibraryZip = (Resolve-Path -LiteralPath $LibraryZip).Path
$ApprovedOnlyZip = (Resolve-Path -LiteralPath $ApprovedOnlyZip).Path
$repoRoot = (& git rev-parse --show-toplevel 2>$null).Trim()
Assert-CommandSuccess "Cannot locate the Git repository"
if (-not $repoRoot) { throw "Run this script from inside the ebooks Git repository." }
Set-Location $repoRoot

$remote = (& git remote get-url origin 2>$null).Trim()
Assert-CommandSuccess "Cannot read origin remote"
if ($remote -notmatch 'github\.com[:/]htspathe/ebooks(?:\.git)?$') { throw "Unexpected origin remote '$remote'. Expected htspathe/ebooks." }
$currentBranch = (& git branch --show-current).Trim()
if ($currentBranch -ne $ExpectedBranch) { throw "Switch to '$ExpectedBranch' first. Current branch: '$currentBranch'." }
if (& git status --porcelain) { throw "Working tree is not clean. Commit or stash existing changes first." }

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$full = [System.IO.Compression.ZipFile]::OpenRead($LibraryZip)
$approved = [System.IO.Compression.ZipFile]::OpenRead($ApprovedOnlyZip)
$temp = Join-Path ([System.IO.Path]::GetTempPath()) ("roadtrip-illustrations-" + [guid]::NewGuid().ToString("N"))

try {
    Assert-SafeArchive $full $BookPrefix
    Assert-SafeArchive $approved ""
    $fullFiles = @($full.Entries | Where-Object { -not $_.FullName.EndsWith("/") })
    $approvedFiles = @($fullFiles | Where-Object { $_.FullName.StartsWith($BookPrefix + "assets/approved/") -and $_.FullName.EndsWith(".png") })
    $originalFiles = @($fullFiles | Where-Object { $_.FullName.StartsWith($BookPrefix + "assets/originals/") -and $_.FullName.EndsWith(".png") })
    $rejectedFiles = @($fullFiles | Where-Object { $_.FullName.StartsWith($BookPrefix + "assets/rejected/") -and $_.FullName.EndsWith(".png") })
    $approvedOnlyFiles = @($approved.Entries | Where-Object { -not $_.FullName.EndsWith("/") -and $_.FullName.EndsWith(".png") })
    if ($fullFiles.Count -ne 117) { throw "Expected 117 files in full library; found $($fullFiles.Count)." }
    if ($approvedFiles.Count -ne 58) { throw "Expected 58 approved PNGs in full library; found $($approvedFiles.Count)." }
    if ($originalFiles.Count -ne 34) { throw "Expected 34 original PNGs; found $($originalFiles.Count)." }
    if ($rejectedFiles.Count -ne 2) { throw "Expected 2 archived rejected PNGs; found $($rejectedFiles.Count)." }
    if ($approvedOnlyFiles.Count -ne 58) { throw "Expected 58 PNGs in approved-only archive; found $($approvedOnlyFiles.Count)." }

    foreach ($entry in $approvedOnlyFiles) {
        $fullEntryName = $BookPrefix + "assets/approved/" + $entry.FullName.Replace("\", "/")
        $hashApprovedOnly = Get-ZipEntryHash $approved $entry.FullName
        $hashFullLibrary = Get-ZipEntryHash $full $fullEntryName
        if ($hashApprovedOnly -ne $hashFullLibrary) { throw "Approved image mismatch: $($entry.FullName)" }
    }

    [System.IO.Compression.ZipFile]::ExtractToDirectory($LibraryZip, $temp)
    $source = Join-Path $temp $BookFolder
    if (-not (Test-Path -LiteralPath $source)) { throw "Expected book folder not found after extraction." }
    $destination = Join-Path $repoRoot $BookFolder
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Get-ChildItem -LiteralPath $source -Force | Copy-Item -Destination $destination -Recurse -Force
    $approvedOnDisk = @(Get-ChildItem -LiteralPath (Join-Path $destination "assets/approved") -Recurse -File -Filter "*.png")
    if ($approvedOnDisk.Count -ne 58) { throw "Post-copy check failed: expected 58 approved PNGs, found $($approvedOnDisk.Count)." }

    $statePath = Join-Path $destination "KDP_PROGRESS_STATE.json"
    $state = Get-Content -LiteralPath $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $state.status = "ILLUSTRATION_LIBRARY_IMPORTED_PENDING_LAYOUT"
    $state | Add-Member -Force -MemberType NoteProperty -Name "illustration_library" -Value ([pscustomobject]@{
        status = "IMPORTED_PENDING_LAYOUT"
        source_archive_files = 117
        approved_images = 58
        original_images = 34
        rejected_images_archived = 2
        approved_only_crosscheck = "SHA256_MATCH_58_OF_58"
        image_dpi = 300
        pure_black_white = $true
        visual_review = "PENDING"
        final_page_layout = "NOT_STARTED"
        source_archive = [System.IO.Path]::GetFileName($LibraryZip)
        approved_only_archive = [System.IO.Path]::GetFileName($ApprovedOnlyZip)
    })
    $state.next_step = "Lay out approved illustrations on pages 1, 4, 5-14 and 55-80; use individual 600x600 icons and motifs where appropriate; reconcile the documented P56 bounding-box and Spot-the-Difference dimension discrepancies; visually review all pages; then assemble and validate the 80-page PDF."
    $state | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $statePath -Encoding UTF8

    $readmePath = Join-Path $destination "README.md"
    $readme = Get-Content -LiteralPath $readmePath -Raw -Encoding UTF8
    $newStatus = "- **Statut :** 48 activités programmatiques générées (pages 15–54 et 73–80) ; bibliothèque d’illustrations intégrée (58 images approuvées, 34 originaux et 2 rejets archivés). La mise en page finale, la revue visuelle et le PDF KDP de 80 pages restent à terminer."
    $readme = [regex]::Replace($readme, '(?m)^- \*\*Statut :\*\*.*$', $newStatus)
    if ($readme -notmatch '## Bibliothèque d’illustrations') {
        $readme += @"

## Bibliothèque d’illustrations

La bibliothèque complète est conservée dans art_bible/, assets/originals/, assets/approved/, assets/rejected/, production/ et reports/. Pour la mise en page finale, utiliser exclusivement assets/approved/. Les 58 PNG approuvés ont été comparés par SHA-256 à l’archive IMAGES_APPROVED_ONLY ; les 58 correspondances sont exactes. Les originaux et les rejets restent archivés pour la traçabilité, pas pour l’intérieur final.
"@
    }
    Set-Content -LiteralPath $readmePath -Value $readme -Encoding UTF8

    $paths = @(
        "$BookFolder/art_bible",
        "$BookFolder/assets",
        "$BookFolder/production/ASSET_MANIFEST.csv",
        "$BookFolder/production/DIFFERENCE_LEDGER.csv",
        "$BookFolder/production/GENERATION_LOG.md",
        "$BookFolder/production/ILLUSTRATION_LIBRARY_AUDIT.md",
        "$BookFolder/reports",
        "$BookFolder/KDP_PROGRESS_STATE.json",
        "$BookFolder/README.md"
    )
    git add -- $paths
    Assert-CommandSuccess "Git staging failed"
    git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) { throw "No changes staged. The illustration library may already be imported." }
    git commit -m "kdp: import verified Road Trip illustration library"
    Assert-CommandSuccess "Git commit failed"
    git push -u origin HEAD
    Assert-CommandSuccess "Git push failed"

    Write-Host ""
    Write-Host "IMPORT COMPLETED AND PUSHED" -ForegroundColor Green
    Write-Host "Approved PNGs: 58 (SHA-256 matched 58/58)"
    Write-Host "Original PNGs: 34"
    Write-Host "Rejected PNGs archived: 2"
    Write-Host "Branch: $ExpectedBranch"
    Write-Host "No Amazon publication was performed."
}
finally {
    $full.Dispose()
    $approved.Dispose()
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Recurse -Force }
}
