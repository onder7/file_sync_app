# File Synchronization Application
# Dosya Senkronizasyon Uygulaması

[Türkçe Version](TR-README.md)

## Features
- Folder and file-based synchronization
- Automatic synchronization and scheduling
- Customizable file and folder patterns
- Fast copying with multi-thread support
- Backup functionality
- Detailed logging
- User-friendly interface

## Installation
1. Download the application
2. Install required modules:
   ```
   pip install -r requirements.txt
   ```
3. Start the application:
   ```
   python run.py
   ```

## Usage
1. **Source Folder**: Folder containing files to be synchronized
2. **Target Folder**: Folder where files will be copied
3. **Folder Patterns**: Which folders to synchronize (e.g., "9H-C*")
4. **File Patterns**: Which files to synchronize (e.g., "*.wgl")
5. **Check Interval**: Waiting period for synchronization check (seconds)

## Settings
- **Folder Patterns**: Determines folders to be synchronized
  - Example: "9H-C*" (all folders starting with 9H-C)
  - Use commas for multiple patterns: "9H-C*, TEST*"

- **File Patterns**: Determines files to be synchronized
  - Example: "*.wgl" (all files with wgl extension)
  - Use commas for multiple patterns: "*.wgl, *.txt"

- **Excluded Patterns**: Items to be excluded from synchronization
  - Example: ".git/*, *.tmp"

- **Check Interval**: Synchronization check frequency (seconds)
  - Recommended: 10-60 seconds

- **Thread Count**: Number of parallel copy operations
  - Recommended: 2-8

## Logs
- Logs are kept in the `logs` folder
- Separate log file for each day
- Format: `file_sync_YYYYMMDD.log`

## Backup
- When "Backup Modified Files" option is enabled:
  - Modified files are backed up
  - Backup format: `filename.extension.bak.timestamp`

## Email Notifications
- Email notification for error conditions
- Synchronization summary delivery
- Gmail or custom SMTP server support

## Licensing

- Full version features:
  - Unlimited folder synchronization
  - Email notifications
  - Backup features
  - Priority support

## System Requirements
- Windows 7 or higher
- Minimum 2GB RAM
- Python 3.8 or higher

## Security
- Application works only on specified folders
- Does not interfere with system files
- All operations are logged

## Support and Contact
- Email: onder7@gmail.com
- GitHub: https://github.com/onder7
- Web: https://ondernet.net

## License
This software is distributed under the MIT license.

## Version History
### v2.1.0 (2024-02-29)
- Added email notifications
- Performance improvements
- Bug fixes

### v2.0.0 (2024-02-16)
- Initial release
- Basic synchronization features
- GUI interface
- Logging system
