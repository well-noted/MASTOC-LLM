# run_full_baseline_sweep.ps1
# ============================================================
# Comprehensive psychosocial parameter sweep for MASTOC-LLM.
# Runs all conditions sequentially, saves each CSV individually,
# and concatenates into baseline_sweep_master.csv at the end.
#
# Usage:
#   cd C:\Users\tetuo\OneDrive\Documents\Claude\Projects\MASTOC-LLM
#   .\run_full_baseline_sweep.ps1
# ============================================================

Set-Location $PSScriptRoot

$R   = 20
$TMP = "baseline_sweep_table.csv"
$OUT = "baseline_results"
$masterFile = "baseline_sweep_master.csv"

if (-not (Test-Path $OUT)) { New-Item -ItemType Directory -Path $OUT | Out-Null }

$script:isFirst = $true
$script:nDone   = 0
$start = Get-Date

function Run-Condition($label, $extraArgs) {
    Write-Host ""
    Write-Host "-------------------------------------------" -ForegroundColor DarkCyan
    Write-Host "  $label" -ForegroundColor Cyan
    Write-Host "-------------------------------------------" -ForegroundColor DarkCyan

    $cmd = "python run_baseline_sweep.py --runs $R $extraArgs"
    Write-Host "  > $cmd" -ForegroundColor Gray
    Invoke-Expression $cmd

    # Wait briefly for NetLogo to release the file, then move it
    Start-Sleep -Milliseconds 800
    if (Test-Path $TMP) {
        $dest = Join-Path $OUT "sweep_${label}.csv"
        Copy-Item $TMP $dest -Force

        if ($script:isFirst) {
            Copy-Item $TMP $masterFile -Force
            $script:isFirst = $false
        } else {
            Get-Content $TMP | Select-Object -Skip 7 | Add-Content $masterFile
        }

        # Retry delete a few times if file is still locked
        $retries = 5
        while ($retries -gt 0) {
            try {
                Remove-Item $TMP -ErrorAction Stop
                break
            } catch {
                Start-Sleep -Milliseconds 500
                $retries--
            }
        }

        $script:nDone++
        Write-Host "  OK  saved to $dest" -ForegroundColor Green
    } else {
        Write-Host "  FAIL  no output file -- run may have failed." -ForegroundColor Red
    }
}


# ===========================================================================
# SWEEP A -- neg_r threshold scan (pos_r=1.0 default)
# Goal: find exact stable->collapse transition as neg_r increases
# ===========================================================================
Write-Host ""
Write-Host "==========================================="
Write-Host "  SWEEP A -- neg_r threshold (pos_r=1.0)"
Write-Host "==========================================="

foreach ($neg_r in @(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)) {
    $nr = [string]([math]::Round($neg_r, 1))
    Run-Condition "A_neg_r$nr" "--neg-r $neg_r"
}


# ===========================================================================
# SWEEP B -- pos_r ablation at two neg_r anchors
# Goal: confirm pos_r=1.0 sustains the default equilibrium;
#       test whether pos_r can compensate for moderate neg_r
# ===========================================================================
Write-Host ""
Write-Host "==========================================="
Write-Host "  SWEEP B -- pos_r ablation"
Write-Host "  (neg_r=0.0 and neg_r=0.5)"
Write-Host "==========================================="

foreach ($neg_r in @(0.0, 0.5)) {
    foreach ($pos_r in @(0.0, 0.25, 0.5, 0.75, 1.0)) {
        $nr = [string]([math]::Round($neg_r, 2))
        $pr = [string]([math]::Round($pos_r, 2))
        Run-Condition "B_neg${nr}_pos${pr}" "--neg-r $neg_r --pos-r $pos_r"
    }
}


# ===========================================================================
# SWEEP C -- neg_r x pos_r full grid (5x5)
# Goal: full Ostrom reciprocity landscape
# ===========================================================================
Write-Host ""
Write-Host "==========================================="
Write-Host "  SWEEP C -- neg_r x pos_r grid (5x5)"
Write-Host "==========================================="

foreach ($neg_r in @(0.0, 0.25, 0.5, 0.75, 1.0)) {
    foreach ($pos_r in @(0.0, 0.25, 0.5, 0.75, 1.0)) {
        $nr = [string]([math]::Round($neg_r, 2))
        $pr = [string]([math]::Round($pos_r, 2))
        Run-Condition "C_neg${nr}_pos${pr}" "--neg-r $neg_r --pos-r $pos_r"
    }
}


# ===========================================================================
# SWEEP D -- risk aversion threshold (neg_r=0 to isolate effect)
# ===========================================================================
Write-Host ""
Write-Host "==========================================="
Write-Host "  SWEEP D -- risk aversion threshold"
Write-Host "  (neg_r=0.0)"
Write-Host "==========================================="

foreach ($risk in @(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)) {
    $rk = [string]([math]::Round($risk, 1))
    Run-Condition "D_risk$rk" "--risk $risk --neg-r 0.0"
}


# ===========================================================================
# SWEEP E -- conformity x neg_r
# Goal: conformity has been 0 throughout -- characterise its effect
# ===========================================================================
Write-Host ""
Write-Host "==========================================="
Write-Host "  SWEEP E -- conformity x neg_r (5x3)"
Write-Host "==========================================="

foreach ($neg_r in @(0.0, 0.5, 1.0)) {
    foreach ($conformity in @(0.0, 0.25, 0.5, 0.75, 1.0)) {
        $nr = [string]([math]::Round($neg_r, 2))
        $cf = [string]([math]::Round($conformity, 2))
        Run-Condition "E_neg${nr}_conf${cf}" "--neg-r $neg_r --conformity $conformity"
    }
}


# ===========================================================================
# SWEEP F -- starting grassland x neg_r
# Goal: does scarcity change the neg_r collapse threshold?
# ===========================================================================
Write-Host ""
Write-Host "==========================================="
Write-Host "  SWEEP F -- starting grassland x neg_r"
Write-Host "==========================================="

foreach ($grass in @(50, 75, 100)) {
    foreach ($neg_r in @(0.0, 0.25, 0.5, 0.75, 1.0)) {
        $nr = [string]([math]::Round($neg_r, 2))
        Run-Condition "F_grass${grass}_neg${nr}" "--grassland $grass --neg-r $neg_r"
    }
}


# ===========================================================================
# SWEEP G -- risk aversion x neg_r (near boundary)
# Goal: does risk aversion shift the pos_r > neg_r collapse threshold?
# Sweep D showed risk has no effect at neg_r=0; this tests the transition zone
# (neg_r=0.75-1.0) where partial collapse already appears.
# ===========================================================================
Write-Host ""
Write-Host "==========================================="
Write-Host "  SWEEP G -- risk aversion x neg_r"
Write-Host "  (boundary region: neg_r = 0.75 to 1.0)"
Write-Host "==========================================="

foreach ($neg_r in @(0.75, 0.8, 0.9, 1.0)) {
    foreach ($risk in @(0.0, 0.25, 0.5, 0.75, 1.0)) {
        $nr = [string]([math]::Round($neg_r, 2))
        $rk = [string]([math]::Round($risk, 2))
        Run-Condition "G_neg${nr}_risk${rk}" "--neg-r $neg_r --risk $risk"
    }
}


# ===========================================================================
# Done
# ===========================================================================
$elapsed = (Get-Date) - $start
Write-Host ""
Write-Host "==========================================="
Write-Host "  ALL SWEEPS COMPLETE"
Write-Host "==========================================="
Write-Host ("  Conditions run : {0}" -f $script:nDone)
Write-Host ("  Total runs     : {0}" -f ($script:nDone * $R))
Write-Host ("  Elapsed        : {0:hh\:mm\:ss}" -f $elapsed)
Write-Host ("  Master CSV     : {0}" -f $masterFile)
Write-Host ("  Per-condition  : {0}\" -f $OUT)
Write-Host "==========================================="
