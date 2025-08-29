# GitHub Actions Build Troubleshooting

## Common Issues and Solutions

### Issue 1: "Unknown command/target android"
**Error**: `buildozer android debug` returns "Unknown command/target android"

**Solution**:
- This means Buildozer doesn't have Android support installed
- The GitHub Actions workflow should handle this automatically
- If it persists, check that all dependencies are installed correctly

### Issue 2: Android SDK License Issues
**Error**: `Skipping following packages as the license is not accepted: Android SDK Build-Tools`

**Solutions**:
1. **Automatic license acceptance**: The workflow now accepts licenses automatically
2. **Manual license acceptance**: If needed, run `yes | sdkmanager --licenses`
3. **Check SDK installation**: Ensure Android SDK is properly downloaded

### Issue 3: NDK Download Fails
**Error**: `ValueError: read of closed file` during NDK download

**Solutions**:
1. **Retry logic**: The workflow now includes automatic retry (3 attempts)
2. **Stable NDK version**: Using recommended NDK version (25b)
3. **Let buildozer handle NDK**: Removed manual NDK installation
4. **Check network**: Ensure stable internet connection for large downloads

### Issue 4: "python-for-android directory not found"
**Error**: `FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/.../python-for-android'`

**Solutions**:
1. **Wait for first build**: The first build downloads python-for-android (~500MB)
2. **Check internet connection**: GitHub Actions needs to download Android SDK/NDK
3. **Increase timeout**: First build can take 45-60 minutes

### Issue 3: Build times out
**Error**: Build exceeds 60-minute timeout

**Solutions**:
1. **First build is slow**: Android SDK/NDK download takes time
2. **Subsequent builds are faster**: ~15-20 minutes after first build
3. **Check logs**: Look for specific errors in the build output

### Issue 4: Dependency installation fails
**Error**: Pip install fails for certain packages

**Solutions**:
1. **Check package compatibility**: Some packages don't work on Android
2. **Simplify requirements**: Remove non-essential packages from buildozer.spec
3. **Use compatible versions**: Check kivy.org for Android-compatible packages

### Issue 5: APK not generated
**Error**: Build completes but no APK in artifacts

**Solutions**:
1. **Check build logs**: Look for errors in the final build steps
2. **Verify file paths**: Ensure bin/ directory is created
3. **Check permissions**: Make sure artifacts can be uploaded

## Build Process Overview

1. **Setup (5-10 min)**: Install dependencies, download Android tools
2. **Build (20-40 min)**: Compile Python code, create APK
3. **Package (2-5 min)**: Sign and package the APK
4. **Upload (1-2 min)**: Upload APK to GitHub artifacts

## Monitoring Your Build

1. **Go to your repository** → **Actions** tab
2. **Click on the running workflow**
3. **Watch the build progress** in real-time
4. **Check the "Build Android APK" step** for detailed logs

## Useful Commands for Local Testing

```bash
# Test if buildozer works
buildozer --version

# Check available targets
buildozer --help

# Clean previous builds
buildozer android clean

# Just download dependencies (faster testing)
buildozer android update
```

## Alternative Build Methods

If GitHub Actions doesn't work:

### Option A: Use Docker Locally
```bash
# If you can get Docker working
docker run --volume "$(pwd)":/home/user/hostcwd kivy/buildozer buildozer android debug
```

### Option B: Use Online Services
- **Pydroid Repository**: Build APK directly on Android
- **Buildozer Online**: Web-based APK builder
- **GitLab CI**: Alternative to GitHub Actions

### Option C: Local Linux VM
- Install Ubuntu in VirtualBox/VMware
- Install Buildozer in the VM
- Build APK locally

## Getting Help

1. **Check Buildozer documentation**: https://buildozer.readthedocs.io/
2. **Kivy forums**: https://groups.google.com/g/kivy-users
3. **GitHub Issues**: Check existing issues in buildozer repository
4. **Stack Overflow**: Search for specific error messages

## Performance Tips

- **First build**: 45-60 minutes (downloads Android SDK/NDK)
- **Subsequent builds**: 15-20 minutes (reuses downloaded tools)
- **Clean builds**: Use `buildozer android clean` only when necessary
- **Cache dependencies**: GitHub Actions caches pip packages automatically

## File Structure for Successful Build

Ensure your repository has:
```
📁 your-repo/
├── 📄 main.py (main application file)
├── 📄 buildozer.spec (build configuration)
├── 📄 README.md (documentation)
├── 📁 .github/
│   └── 📁 workflows/
│       └── 📄 build.yml (GitHub Actions)
└── 📄 (other Python files)
```

## Success Indicators

✅ **Build completes** without errors
✅ **APK file appears** in bin/ directory
✅ **Artifacts uploaded** to GitHub Actions
✅ **Download link** available in Actions → Artifacts

Remember: Building Android apps is complex and the first build always takes the longest. Be patient and check the logs for specific error messages!