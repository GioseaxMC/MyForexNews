@echo on
REM Initialize a new Git repository

REM Step 1: Initialize Git repository
git init

REM Step 2: Add a .gitignore file (you can modify this part to add specific ignores)
echo # Ignore temporary files > .gitignore
echo dummy.py >> .gitignore
echo /__pycache__ >> .gitignore
echo gitstart.bat >> .gitignore

REM Step 3: Add all files to the repository
git add .

REM Step 4: Commit the changes
git commit -m "Initial commit"

REM Step 5: Add the remote repository (replace with your actual remote URL)
git remote add origin https://github.com/GioseaxMC/MyForexNews

git pull origin main --allow-unrelated-histories


REM Step 6: Push the changes to the remote repository (main branch)
git push -u origin main

echo Repository initialized and pushed to remote.
pause
