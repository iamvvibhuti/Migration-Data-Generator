
import argparse
import base64
import csv
import hashlib
import io
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import format_datetime
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

BASE = Path(__file__).resolve().parent
KEY = BASE / "service-account.json"
USERS = BASE / "users.txt"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.insert",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive.file",
]

SUBJECTS = [
    "FYI - data migration update",
    "Action needed: API rate limits",
    "Fwd: team offsite",
    "Fwd: partner agreement",
    "Invoice review - quarterly OKRs",
    "Q3 planning sync notes",
    "Re: data migration follow-up",
    "Draft proposal - data migration",
    "Budget review follow-up",
    "Weekly status - press release",
    "Re: localization",
    "Migration validation report",
]

CUSTOM_LABELS = [
    "Migration-Test",
    "Project-Avengers",
    "Clients/VIP",
    "Archive/2023",
]

GMAIL_COLUMNS = [
    "Owner", "Correspondent", "Correspondent Type", "Date",
    "Subject", "Labels", "Custom Label", "Size (bytes)",
    "SHA256", "Attachment Name", "Attachment SHA256",
    "Gmail Message ID", "RFC822 Message ID", "Migration Test ID",
]

DRIVE_COLUMNS = [
    "Owner", "File Name", "File Type", "File ID", "File URL",
    "Size (bytes)", "SHA256", "Scenario", "Sharing Type",
    "Sharing Detail", "Migration Test ID",
]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_users():
    users = [
        line.strip()
        for line in USERS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not users:
        raise ValueError("Add at least one account to users.txt.")
    if len(users) != len(set(users)):
        raise ValueError("Duplicate accounts in users.txt.")
    return users


def services(owner):
    creds = service_account.Credentials.from_service_account_file(
        str(KEY), scopes=SCOPES
    ).with_subject(owner)
    return (
        build("gmail", "v1", credentials=creds, cache_discovery=False),
        build("drive", "v3", credentials=creds, cache_discovery=False),
    )


def ensure_labels(gmail):
    existing = gmail.users().labels().list(userId="me").execute()
    labels = {x["name"]: x["id"] for x in existing.get("labels", [])}

    for name in CUSTOM_LABELS:
        if name not in labels:
            result = gmail.users().labels().create(
                userId="me",
                body={
                    "name": name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                },
            ).execute()
            labels[name] = result["id"]

    return labels


def make_attachment(index, run_id):
    # Small, real CSV attachment with a deterministic structure.
    name = f"filler-{index:04d}.csv"
    content = (
        "test_id,status,scenario\n"
        f"{run_id}-{index:05d},TEST,synthetic\n"
        f"{run_id}-{index:05d}-b,VALIDATION,synthetic\n"
    ).encode("utf-8")
    return name, content


def make_email(gmail, owner, run_id, index, rng, custom_labels):
    test_id = str(uuid.uuid4())
    subject = rng.choice(SUBJECTS)
    correspondent_type = rng.choice([
        "Internal test user",
        "External synthetic identity",
        "Non-migrating test identity",
    ])

    # Use reserved example domains for synthetic identities.
    if correspondent_type == "Internal test user":
        correspondent = owner
        sender = owner
        recipient = owner
    elif correspondent_type == "External synthetic identity":
        correspondent = f"external-{index}@example.net"
        sender = correspondent
        recipient = owner
    else:
        correspondent = f"archive-{index}@example.org"
        sender = correspondent
        recipient = owner

    # Spread dates across the last several years.
    date = datetime.now(timezone.utc) - timedelta(
        days=rng.randint(0, 2500),
        seconds=rng.randint(0, 86399),
    )

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg["Date"] = format_datetime(date)
    msg["Message-ID"] = f"<{test_id}@migration-test.invalid>"

    body = (
        "Synthetic message for authorized Workspace migration testing.\n\n"
        f"Migration Test ID: {test_id}\n"
        f"Owner: {owner}\n"
        f"Correspondent Type: {correspondent_type}\n"
        f"Scenario: {subject}\n"
        "No real customer or employee information is included.\n"
    )
    msg.set_content(body)

    attachment_name = ""
    attachment_hash = ""
    if index % 5 == 0:
        attachment_name, attachment = make_attachment(index, run_id)
        msg.add_attachment(
            attachment,
            maintype="text",
            subtype="csv",
            filename=attachment_name,
        )
        attachment_hash = sha256(attachment)

    raw_bytes = msg.as_bytes()
    raw = base64.urlsafe_b64encode(raw_bytes).decode("ascii")

    # Select a variety of standard labels and states.
    label_ids = ["INBOX"]
    if index % 4 == 0:
        label_ids.append("UNREAD")
    if index % 7 == 0:
        label_ids.append("STARRED")
    if index % 9 == 0:
        label_ids.append("IMPORTANT")

    custom_name = ""
    if index % 3 == 0:
        custom_name = CUSTOM_LABELS[index % len(CUSTOM_LABELS)]
        label_ids.append(custom_labels[custom_name])

    result = gmail.users().messages().insert(
        userId="me",
        body={"raw": raw, "labelIds": label_ids},
        internalDateSource="dateHeader",
    ).execute(num_retries=5)

    return {
        "Owner": owner,
        "Correspondent": correspondent,
        "Correspondent Type": correspondent_type,
        "Date": date.isoformat(),
        "Subject": subject,
        "Labels": ",".join(label_ids),
        "Custom Label": custom_name,
        "Size (bytes)": len(raw_bytes),
        "SHA256": sha256(raw_bytes),
        "Attachment Name": attachment_name,
        "Attachment SHA256": attachment_hash,
        "Gmail Message ID": result["id"],
        "RFC822 Message ID": msg["Message-ID"],
        "Migration Test ID": test_id,
    }


def make_pdf(test_id):
    # Minimal valid one-page PDF for migration testing.
    text = f"Synthetic migration test {test_id}"
    stream = f"BT /F1 12 Tf 50 750 Td ({text}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for n, obj in enumerate(objects, 1):
        offsets.append(len(out))
        out.extend(f"{n} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects)+1}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(
        f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(out)


def make_drive_content(index, run_id):
    test_id = str(uuid.uuid4())
    extension = ["txt", "csv", "json", "pdf", "bin"][index % 5]
    if extension == "txt":
        content = (
            f"Synthetic migration test\nID: {test_id}\n"
            "Environment: SOURCE\n"
        ).encode()
        mime = "text/plain"
    elif extension == "csv":
        content = (
            "test_id,status\n"
            f"{test_id},TEST\n"
            f"{test_id},VALIDATION\n"
        ).encode()
        mime = "text/csv"
    elif extension == "json":
        content = json.dumps({
            "migration_test_id": test_id,
            "run_id": run_id,
            "synthetic": True,
        }, indent=2).encode()
        mime = "application/json"
    elif extension == "pdf":
        content = make_pdf(test_id)
        mime = "application/pdf"
    else:
        # Synthetic binary filler, not a real PNG image.
        content = (
            f"SYNTHETIC-BINARY-{test_id}-".encode()
            + bytes([index % 256]) * (1024 + (index % 10) * 1024)
        )
        mime = "application/octet-stream"
    return test_id, extension, content, mime


def create_drive_file(drive, owner, run_id, index, folder_id):
    test_id, extension, content, mime = make_drive_content(index, run_id)
    name = f"{test_id[:8]}-filler.{extension}"
    media = MediaIoBaseUpload(
        io.BytesIO(content), mimetype=mime, resumable=False
    )
    result = drive.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media,
        fields="id,name,mimeType,size,webViewLink",
    ).execute(num_retries=5)

    return {
        "Owner": owner,
        "File Name": name,
        "File Type": mime,
        "File ID": result["id"],
        "File URL": result.get(
            "webViewLink",
            f"https://drive.google.com/file/d/{result['id']}/view",
        ),
        "Size (bytes)": len(content),
        "SHA256": sha256(content),
        "Scenario": "binary" if extension == "bin" else extension,
        "Sharing Type": "Private (not shared)",
        "Sharing Detail": "N/A",
        "Migration Test ID": test_id,
    }


def write_csv(path, columns, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emails", type=int, default=10)
    parser.add_argument("--files", type=int, default=5)
    args = parser.parse_args()

    if args.emails < 0 or args.files < 0:
        parser.error("Counts must be non-negative.")
    if not KEY.exists():
        raise FileNotFoundError(f"Missing {KEY}")

    users = load_users()
    run_id = str(uuid.uuid4())
    gmail_rows = []
    drive_rows = []

    for owner in users:
        print(f"Processing {owner}")
        gmail, drive = services(owner)
        labels = ensure_labels(gmail)

        for i in range(1, args.emails + 1):
            row = make_email(gmail, owner, run_id, i, random.Random(i), labels)
            gmail_rows.append(row)
            if i % 100 == 0:
                print(f"  Gmail: {i}/{args.emails}")

        folder = drive.files().create(
            body={
                "name": f"MIGRATION-TEST-{run_id[:8]}",
                "mimeType": "application/vnd.google-apps.folder",
            },
            fields="id",
        ).execute()["id"]

        for i in range(1, args.files + 1):
            drive_rows.append(
                create_drive_file(drive, owner, run_id, i, folder)
            )
            if i % 100 == 0:
                print(f"  Drive: {i}/{args.files}")

    write_csv(BASE / "gmail_inventory.csv", GMAIL_COLUMNS, gmail_rows)
    write_csv(BASE / "drive_inventory.csv", DRIVE_COLUMNS, drive_rows)

    print("Finished.")
    print(f"Run ID: {run_id}")
    print(f"Gmail inventory rows: {len(gmail_rows)}")
    print(f"Drive inventory rows: {len(drive_rows)}")
    print("Created gmail_inventory.csv and drive_inventory.csv")


if __name__ == "__main__":
    main()
