# type: ignore
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from src.configs.settings import Settings

import os


class GoogleDriveClient:
    parent_folder_id: str | None
    scope: str | None

    def __init__(self, credentials_path: str):
        self.parent_folder_id = Settings.GOOGLE_DRIVE_FOLDER_ID
        self.scope = Settings.GOOGLE_DRIVE_SCOPE
        self.credentials = (
            service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=[self.scope],
            )
        )
        self.service = build("drive", "v3", credentials=self.credentials)

    def create_folder(self, folder_name: str) -> str:
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if self.parent_folder_id:
            folder_metadata["parents"] = [self.parent_folder_id]

        new_folder = self.service.files().create(body=folder_metadata).execute()
        # return new_folder["id"]
        print(f"Folder '{folder_name}' created with ID: {new_folder['id']}")

    def upload_file(self, file_path: str, folder_id: str) -> str:
        file_metadata = {
            "name": os.path.basename(file_path),
            "parents": [folder_id],
        }
        media = MediaFileUpload(file_path)
        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media)
            .execute()
        )
        print(
            f"File '{os.path.basename(file_path)}' uploaded with ID: {file['id']}"
        )
