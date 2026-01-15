# Git push script for Phase 3
Write-Host "Adding files to git..." -ForegroundColor Cyan
git add .

Write-Host "Committing changes..." -ForegroundColor Cyan
git commit -m "Phase 3: Enhanced Safety - Backups, rollback, dry-run, change tracking, sandbox, restore points"

Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push

Write-Host "Done!" -ForegroundColor Green
