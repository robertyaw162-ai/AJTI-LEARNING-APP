AJTI LEARNING APP VERSION 6.0 — ANDROID APK PROJECT

This folder contains:
- main.py: AJTI Learning App Python source
- buildozer.spec: Android packaging settings
- .github/workflows/build-apk.yml: cloud build workflow for creating an APK

IMPORTANT
- This ZIP is a project to build an APK; it is NOT itself an APK.
- I checked Python syntax. I have not compiled or run the APK, and the cloud build may need troubleshooting.
- School badge and colours are placeholders until the official branding is supplied.
- This is a learning prototype. Do not use real sensitive passwords or personal data.

PHONE-ONLY BUILD PATH (requires a GitHub account)
1. Extract this ZIP on your phone.
2. Create a new repository on GitHub.
3. Upload the extracted project files/folders into the repository, keeping the .github/workflows/build-apk.yml path.
4. Open the repository's Actions tab and enable Actions if asked.
5. Run the workflow named "Build AJTI Android APK" using "Run workflow", or push/commit to the main branch.
6. Wait for the workflow to finish. If it fails, open the failed job and read the first error.
7. If successful, open the completed workflow run, scroll to Artifacts, and download "AJTI-Learning-App-V6-APK".
8. Extract the downloaded artifact ZIP to get the .apk file. Send the APK to your friends.
9. On each Android phone, the owner may need to allow installation from the app used to open the APK. Only install APKs from people you trust.

NOTE
The first build may take several minutes and can fail if Android toolchain versions or dependencies change. This workflow is a prepared starting point, not a guarantee that compilation will succeed.
