Workspace Migration Test Data Generator

1. Project Overview

This project generates synthetic email messages and cloud storage files to test workspace migrations. It helps administrators populate authorized source test accounts and create CSV inventories that can be opened in Microsoft Excel.

The inventories record generated message and file metadata to support migration validation, auditing, and troubleshooting.

Current Capabilities

Generate synthetic email messages through an email API.
Create email labels and apply selected labels to messages.
Generate email messages with synthetic CSV attachments.
Create cloud storage folders and synthetic TXT, CSV, JSON, PDF, and binary files.
Calculate SHA-256 hashes of generated content.
Record returned email message IDs and storage file IDs.
Export email and storage inventories to CSV.
Support one or more configured test accounts.
Current Limitations

The current advanced script does not provide complete duplicate protection, automatic recovery after partial failures, genuine email conversation threads, or implemented file-sharing scenarios.

Inventory CSV files are overwritten on each execution.

Important: Do not assume a batch is safe to repeat after an error. Verify what was created before restarting.

2. Requirements

A Windows computer.
Python 3.10 or later.
Authorized administrator access to the source workspace.
A cloud project with the required email and storage APIs enabled.
A service account configured for domain-wide delegation.
Appropriate delegation permissions authorized by a workspace super administrator.
One or more authorized source test accounts.
Use synthetic data only. Do not use real employee messages, customer information, or confidential documents.

3. Cloud Configuration

Create or select a dedicated cloud project.
Enable the required email and cloud storage APIs.
Create a dedicated service account.
Enable domain-wide delegation for the service account.
Record the service account's numeric OAuth client ID.
In the source workspace administration console, locate the domain-wide delegation settings under the security and API access controls.
Authorize the client ID with the following OAuth scopes required by the script:
https://www.googleapis.com/auth/gmail.insert
https://www.googleapis.com/auth/gmail.modify
https://www.googleapis.com/auth/drive.file
Review the requested permissions against your organization's security policy before authorizing them.
The script uses delegated access to act as configured users. Authorize this access only for projects and accounts you are permitted to administer.

Create a service-account JSON key only if your organization's policy permits key-based authentication. Store it locally as service-account.json in the project root.

Never upload the key to a source repository or share it in chat.

4. Install the Project on Windows

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
Replace the example with a real test account address in your source workspace.

5. Run a Small Pilot

From Command Prompt, run:


bat
cd C:\WorkspaceMigrationTest
.venv\Scripts\python.exe populate_workspace_advanced.py --emails 10 --files 5
For one configured account, the script attempts to create 10 email messages and 5 storage files.

Verify that the messages and files appear in the correct account. Inspect the following inventory files:

gmail_inventory.csv
drive_inventory.csv
The advanced script writes fresh inventory CSV files for the current execution. Back up earlier inventories before another run.

6. Generate a Larger Batch

For one configured account, run:


bat
.venv\Scripts\python.exe populate_workspace_advanced.py --emails 2000 --files 500
This requests 2,000 new email messages and 500 storage files for each account listed in users.txt.

If five accounts are listed, the requested batch is:

10,000 email messages in total.
2,500 storage files in total.
These counts apply to each execution, not to final mailbox or storage totals. Existing pilot and advanced-test data remain in place.

Important: The current script does not resume safely after a partial failure and does not prevent duplicates across executions. If an error occurs, do not rerun the same command until you have checked the audit records and actual source data.

7. Add or Remove Test Accounts

Open users.txt in Notepad.

To add an account, add its authorized source email address on a new line.

To remove an account, delete its line and save the file.

Example with two accounts:


text
testuser1@your-source-domain.example
testuser2@your-source-domain.example
The script processes every account in this file. Use a one-line users.txt file when running a batch for only one user.

Removing an address from the file stops future script executions from targeting that account. It does not delete previously generated email messages, storage files, or permissions.

Before adding another user, verify that the account exists in the source workspace and that the service account is authorized to act on it.

8. Understand the Inventory Files

Email Inventory

The gmail_inventory.csv file contains fields such as:

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
Storage Inventory

The drive_inventory.csv file contains fields such as:

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
These inventories are generated records, not independent proof of successful migration. Some values describe the generated source content rather than data read back from the source service after storage.

9. Validate the Migration

After generating the source test data:

Confirm that the email messages and storage files exist in the source accounts.
Preserve the inventories associated with the batch being tested.
Configure the migration process with the correct source-to-destination account mapping.
Run the migration according to your organization's approved procedure.
Inspect migration logs and errors.
Compare source and destination message counts, attachments, file counts, file contents, and folder structure.
Record any discrepancies for investigation.
Do not treat the existence of an inventory file as confirmation that every object migrated successfully.

10. Security Rules

Never commit service-account.json, private keys, access tokens, or passwords.
Never commit a real users.txt file.
Never commit sensitive inventories or migration logs.
Keep the repository private unless public distribution has been approved.
Grant repository access only to colleagues who need it.
Use a dedicated test project and synthetic data.
Revoke test credentials when the project is no longer required.
11. Troubleshooting

Python Is Not Recognized

Run:


bat
py --version
If neither python nor py works, install Python and reopen Command Prompt.

Service Account File Not Found

Confirm that service-account.json exists in the directory containing the script.

Authorization or Permission Errors

Check:

API enablement.
The delegated client ID.
Authorized OAuth scopes.
The impersonated user's address.
Workspace security policies.
Incorrect Number of Users

Check users.txt. It must contain the intended accounts, one per line. The advanced script accepts one or more accounts.

Script Stopped During Execution

Do not immediately repeat the full command. Check the latest output, inventory files, and actual source email and storage data first.

Inventory CSV Files Were Replaced

Restore the backup if needed. Copy previous inventories to a separate, protected location before running another batch.

12. Recommended Improvements

Before using this project for repeated large-scale testing, implement:

Persistent run manifests and safe resume.
Duplicate detection and idempotent batch handling.
Inventory append mode with unique run IDs.
Independent source verification and destination comparison.
Genuine email threads and more realistic attachment formats.
Controlled storage-sharing tests between authorized test users.
Automated tests and pinned dependencies.
These improvements must be implemented and tested before claiming that repeated executions are duplicate-safe.

13. License and Intended Use

This project is intended for authorized workspace migration testing using synthetic data.

Follow your organization's security requirements and all applicable API policies. Use the project only with accounts, data, and infrastructure you are authorized to administer.