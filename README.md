Google Workspace Migration Test Data Generator

Generate synthetic Gmail messages and Google Drive files to test Google Workspace migrations using CloudM Migrate.

1. Project objectives

This project helps administrators populate authorized source Workspace test accounts with synthetic data and create CSV inventories that can be opened in Microsoft Excel.

The inventories record generated message and file metadata to support migration testing and troubleshooting.

Current capabilities
Generate synthetic Gmail messages using the Gmail API.
Create Gmail labels and apply selected message labels.
Generate messages with synthetic CSV attachments.
Create Drive folders and synthetic TXT, CSV, JSON, PDF, and binary files.
Calculate SHA-256 hashes of generated content.
Record returned Gmail message IDs and Drive file IDs.
Export Gmail and Drive inventories to CSV.
Support one or more configured test accounts.
Current limitations

The current advanced script does not provide complete duplicate protection, automatic recovery after partial failures, genuine Gmail conversation threads, or implemented Drive-sharing scenarios. Its inventory CSV files are overwritten on each execution.

Do not assume a batch is safe to repeat after an error. Verify what was created before restarting.

2. Requirements
A Windows computer.
Python 3.10 or later.
Authorized administrator access to the source Google Workspace domain.
A Google Cloud project with the Gmail API and Drive API enabled.
A service account configured for domain-wide delegation.
Appropriate domain-wide delegation scopes authorized by a Workspace Super Admin.
One or more authorized source test accounts.

Use synthetic data only. Do not use real employee messages, customer information, or confidential documents.

3. Google Cloud configuration
Create or select a dedicated Google Cloud project.
Enable the Gmail API and Google Drive API.
Create a dedicated service account.
Enable domain-wide delegation for the service account.
Record the service account's numeric OAuth client ID.
In the source Workspace Admin console, open Security > Access and data control > API controls > Manage Domain Wide Delegation.
Authorize the client ID with the OAuth scopes required by the script:
https://www.googleapis.com/auth/gmail.insert
https://www.googleapis.com/auth/gmail.modify
https://www.googleapis.com/auth/drive.file
Review these permissions against your organization's security policy before authorizing them.

The script uses delegated access to act as the configured users. Only authorize this for a project and accounts you are permitted to administer.

Create a service-account JSON key only if your organization's policy permits key-based authentication. Store it locally as service-account.json in the project root. Never upload the key to GitHub or share it in chat.

4. Install the project on Windows

Open Command Prompt and run:

bat
cd C:\
mkdir WorkspaceMigrationTest
cd C:\WorkspaceMigrationTest

py --version
py -m venv .venv

.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install google-api-python-client google-auth


Download or copy these local files into C:\WorkspaceMigrationTest:

populate_workspace_advanced.py
service-account.json
users.txt

The users.txt file must contain one authorized source test account per line.

Example:

text
testuser1@your-source-domain.example


Replace the example with a real test account address in your source Workspace domain.

5. Run a small pilot

From Command Prompt:

bat
cd C:\WorkspaceMigrationTest
.venv\Scripts\python.exe populate_workspace_advanced.py --emails 10 --files 5


For one configured account, the script attempts to create 10 Gmail messages and 5 Drive files.

Verify that the messages and files appear in the correct account. Also inspect gmail_inventory.csv and drive_inventory.csv.

The advanced script writes fresh inventory CSVs for the current execution. Back up earlier inventories before another run.

6. Generate a larger batch

For one configured account:

bat
.venv\Scripts\python.exe populate_workspace_advanced.py --emails 2000 --files 500


This requests 2,000 new Gmail messages and 500 new Drive files for each account listed in users.txt.

If five accounts are listed, the requested batch is 10,000 messages and 2,500 Drive files in total.

The counts are per execution, not final mailbox totals. Existing pilot and advanced-test data remain in place.

Important: The current script does not resume safely after partial failure and does not prevent duplicates across executions. If an error occurs, do not rerun the same command until you have checked the audit records and actual Google data.

7. Add or remove test accounts

Open users.txt in Notepad.

To add an account, add its authorized source email address on a new line.

To remove an account, delete its line.

Save the file before running the script.

Example with two accounts:

text
testuser1@your-source-domain.example
testuser2@your-source-domain.example


The script processes every account in this file. Therefore, use a one-line users.txt file when you want to run a batch for just one user.

Removing an address from the file only stops future script runs from targeting that account. It does not delete previously generated Gmail messages, Drive files, or permissions.

Before adding another user, verify that the account exists in the source Workspace domain and that the service account is authorized to act on it.

8. Understand the inventory files
Gmail inventory

gmail_inventory.csv contains fields such as:

Owner
Correspondent
Correspondent Type
Date
Subject
Labels
Custom Label
Size (bytes)
SHA256
Attachment Name
Attachment SHA256
Gmail Message ID
RFC822 Message ID
Migration Test ID
Drive inventory

drive_inventory.csv contains fields such as:

Owner
File Name
File Type
File ID
File URL
Size (bytes)
SHA256
Scenario
Sharing Type
Sharing Detail
Migration Test ID

These are generated inventories, not independent proof of successful migration. Some values describe the generated source content rather than data read back from Google after storage.

9. Validate CloudM Migrate

After generating the source test data:

Confirm the Gmail messages and Drive files exist in the source accounts.
Preserve the inventories from the batch being tested.
Configure CloudM Migrate with the correct source-to-destination account mapping.
Run the migration according to your organization's approved procedure.
Inspect migration logs and errors.
Compare source and destination message counts, attachments, file counts, file contents, and folder structure.
Record any discrepancies for investigation.

Do not treat the inventory's presence alone as confirmation that every object migrated successfully.

10. Security rules
Never commit service-account.json, private keys, access tokens, or passwords.
Never commit a real users.txt file.
Never commit sensitive inventories or migration logs.
Keep the repository private unless public distribution has been approved.
Grant repository access only to colleagues who need it.
Use a dedicated test project and synthetic data.
Revoke test credentials when the project is no longer required.
11. Troubleshooting
Python is not recognized

Try:

bat
py --version


If neither python nor py works, install Python and reopen Command Prompt.

Service account file not found

Confirm that service-account.json exists in the directory containing the script.

Authorization or permission errors

Check API enablement, the delegated client ID, authorized scopes, the impersonated user's address, and Workspace security policies.

Wrong number of users

Check users.txt. It must contain the intended accounts, one per line. The advanced script accepts one or more accounts.

Script stopped during execution

Do not immediately repeat the full command. Check the latest output, inventory files, and actual source Gmail and Drive data first.

Inventory CSVs were replaced

Restore the backup if needed. Copy previous inventories to a separate, protected location before running another batch.

12. Recommended improvements

Before using this project for repeated large-scale testing, implement:

Persistent run manifests and safe resume.
Duplicate detection and idempotent batch handling.
Inventory append mode with unique run IDs.
Independent source verification and destination comparison.
Genuine email threads and more realistic attachment formats.
Controlled Drive-sharing tests between authorized test users.
Automated tests and pinned dependencies.

These improvements should be tested before claiming that repeated executions are duplicate-safe.

License and intended use

This project is intended for authorized Google Workspace migration testing with synthetic data. Follow your organization's security requirements and Google's applicable API policies.