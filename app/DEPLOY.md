# Deploying to Vercel

The web application directory (`app/`) is configured and ready for 1-click deployment to Vercel with [vercel.json](file:///c:/Users/amang/Downloads/zekathon%201/zekathon/app/vercel.json).

---

## Option 1: Instant Deployment via Terminal (CLI)

Open PowerShell or Command Prompt in the project folder and run:

```powershell
cd app
npx vercel
```

### Steps during the prompt:
1. **Log in**: Vercel will give you a link or open your browser to log in with GitHub/GitLab/Email.
2. **Set up and deploy?**: Press `Y`.
3. **Which scope?**: Select your account.
4. **Link to existing project?**: Press `N`.
5. **Project name**: Press `Enter` (e.g. `zekathon-finance-app`).
6. **In which directory is your code located?**: Press `Enter` (default `./`).
7. **Want to modify settings?**: Press `N`.

Vercel will output your live deployment URL immediately (e.g. `https://zekathon-finance-app.vercel.app`).

To deploy directly to production later:
```powershell
npx vercel --prod
```

---

## Option 2: Continuous Deployment via GitHub (Recommended)

1. Push this repository to GitHub:
   ```powershell
   git remote add origin https://github.com/<YOUR_USERNAME>/zekathon.git
   git push -u origin audit-and-repair
   ```
2. Go to [vercel.com/new](https://vercel.com/new).
3. Import your GitHub repository.
4. In **Root Directory**, click **Edit** and choose `app`.
5. Click **Deploy**.

Vercel will automatically build and publish your site with a custom domain and automatic HTTPS.
