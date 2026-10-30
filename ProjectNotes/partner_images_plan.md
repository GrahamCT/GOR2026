# Partner Images → Azure Blob Storage

## Problem

Partner logo and landing images are saved to `app/static/partners/` inside the running container.
Every deploy (`deploy.bat` / `deploy-prod.bat`) builds a fresh image from the local folder, so any
image uploaded on QA or prod since the last deploy is lost.

## Decision

Split `app/static` into two kinds of file:

| Kind | Examples | Lives in |
|---|---|---|
| Design assets | `v2/` heroes, fonts, logos, `fav.png` | `app/static`, committed to git, shipped with each deploy (unchanged) |
| Content | `partners/` logos and landing images | Azure Blob Storage, one container per environment |

The DB keeps storing relative paths (`partners/logo_cat1_spur.png`). A template helper turns that
path into a full blob URL, so **no DB change is needed**.

```
DB value:        partners/logo_cat1_spur.png
MEDIA_BASE_URL:  https://gor2026media.blob.core.windows.net/gor-qa/
Rendered URL:    https://gor2026media.blob.core.windows.net/gor-qa/partners/logo_cat1_spur.png
```

---

## Part 1 — Azure setup (one-off)

Existing resources: resource group `DEVOPS`, web apps `gor26-Q` (QA) and `gor26-P` (prod).
`gor2026media` below is a placeholder. Storage account names must be globally unique,
3–24 chars, lowercase letters and digits only.

### 1.1 Find the region the web apps run in

```bash
az webapp show --name gor26-Q --resource-group DEVOPS --query location -o tsv
```

Use the same region for the storage account so images are served close to the app.

### 1.2 Create the storage account

```bash
az storage account create \
  --name gor2026media \
  --resource-group DEVOPS \
  --location <region from 1.1> \
  --sku Standard_LRS \
  --kind StorageV2 \
  --min-tls-version TLS1_2 \
  --allow-blob-public-access true
```

`--allow-blob-public-access true` is required: new accounts block anonymous read by default,
and browsers need to load the images without credentials.

Portal equivalent: *Storage accounts → Create* → Standard / LRS, then
*Configuration → Allow Blob anonymous access → Enabled*.

### 1.3 Create one container per environment

```bash
az storage container create --account-name gor2026media --name gor-qa   --public-access blob --auth-mode login
az storage container create --account-name gor2026media --name gor-prod --public-access blob --auth-mode login
```

`--public-access blob` lets anyone read a blob if they know its URL, but nobody can list the
container. That's the right level for public partner images.

If `--auth-mode login` fails with a permissions error, give yourself the data role once:

```bash
az role assignment create \
  --assignee <your-azure-login-email> \
  --role "Storage Blob Data Contributor" \
  --scope $(az storage account show --name gor2026media --resource-group DEVOPS --query id -o tsv)
```

### 1.4 Get the connection string (the app uses it to upload)

```bash
az storage account show-connection-string --name gor2026media --resource-group DEVOPS -o tsv
```

Treat it as a secret, like `GOR_CONNECTION`. Don't commit it.

### 1.5 Add app settings to each web app

`.env` is excluded from the Docker image (`.dockerignore`), so these go in the Azure app settings.

```bash
az webapp config appsettings set --name gor26-Q --resource-group DEVOPS --settings \
  AZURE_STORAGE_CONNECTION_STRING="<from 1.4>" \
  MEDIA_CONTAINER="gor-qa" \
  MEDIA_BASE_URL="https://gor2026media.blob.core.windows.net/gor-qa/"

az webapp config appsettings set --name gor26-P --resource-group DEVOPS --settings \
  AZURE_STORAGE_CONNECTION_STRING="<from 1.4>" \
  MEDIA_CONTAINER="gor-prod" \
  MEDIA_BASE_URL="https://gor2026media.blob.core.windows.net/gor-prod/"
```

Hold off on `MEDIA_BASE_URL` until Part 2 is done. Without it the app keeps using `/static/`
(see Part 3), so you can set the other two settings early and switch over by adding this one.

Also add all three to your local `.env` (pointed at `gor-qa`) if you want local dev to use blob storage.
Leave them out to keep using the local `app/static/partners/` folder.

### 1.6 (Later, optional) CDN

Not needed at this traffic level. If it's ever needed, put Azure Front Door in front of the
storage account and change `MEDIA_BASE_URL` to the Front Door hostname. No code change.

---

## Part 2 — Migrate existing images

### 2.1 Rescue images that exist only on the servers

Images uploaded on QA/prod since the last deploy exist only inside the running container, and the
next deploy deletes them. Before deploying anything else:

1. List every image path the DB references, on both QA and prod:
   ```sql
   SELECT id, partner_name, logo_image, landing_image FROM book_Partner
   ```
2. Compare against local `app/static/partners/` (about 200 files, about 30 MB).
3. For any that are missing locally, open them in a browser at
   `https://<app>.azurewebsites.net/static/partners/<file>` and save them, or ask the person who
   uploaded them for the originals.

### 2.2 Upload to each container

```bash
az storage blob upload-batch \
  --account-name gor2026media \
  --destination gor-qa \
  --destination-path partners \
  --source app/static/partners \
  --content-cache-control "public, max-age=31536000" \
  --auth-mode login
```

Repeat with `--destination gor-prod`. If QA and prod use different image sets, upload each from the
right source.

`upload-batch` sets the correct `Content-Type` from each file extension. Without that, browsers
download the image instead of displaying it.

### 2.3 Check

Open one image in a browser:
`https://gor2026media.blob.core.windows.net/gor-qa/partners/<a filename from the DB>`

---

## Part 3 — Code changes

### 3.1 Dependency

Add to `requirements.txt`:

```
azure-storage-blob==<current version>
```

### 3.2 New service: `app/services/media.py`

- `upload_image(upload: UploadFile, blob_path: str) -> None`. Uploads to `MEDIA_CONTAINER` with
  `ContentSettings(content_type=..., cache_control="public, max-age=31536000")`.
  If `AZURE_STORAGE_CONNECTION_STRING` isn't set, writes to `app/static/<blob_path>` instead
  (the current behaviour, for local dev).
- `media_url(path) -> str`. Returns `MEDIA_BASE_URL + path`, or `/static/` + path if
  `MEDIA_BASE_URL` isn't set. Returns `""` for an empty path, so the templates' placeholder
  fallback still works.

### 3.3 Register the helper in `app/core/templates.py`

```python
from app.services.media import media_url
templates.env.globals["media_url"] = media_url
```

### 3.4 Upload code: `app/routers/partner_admin.py`

- `_save_upload` calls `media.upload_image(...)` instead of `open()` + `shutil.copyfileobj`.
- **Add a timestamp to the filename** so a replaced image gets a new URL and browsers/CDN don't
  keep showing the old one:
  `logo_cat1_spur_20261029143000.png`
- **Validate** before uploading: allow only `.png .jpg .jpeg .webp .svg`, and cap the size
  (for example 5 MB).
- Remove `STATIC_PARTNERS_DIR`.

Old blobs aren't deleted when an image is replaced. Storage is cheap, and keeping them gives a
history. A cleanup script can come later if needed.

### 3.5 Templates: replace `url_for('static', path=X)` with `media_url(X)`

| File | Lines |
|---|---|
| `benefits_v2/_partners.html` | 33 |
| `benefits_v2/_partner_detail.html` | 26, 33 |
| `benefits_v2/partner.html` | 14, 20 |
| `benefits_v2/_booking_voucher.html` | 25 |
| `benefits/_partners.html` | 35 |
| `benefits/_partner_detail.html` | 26, 33 |
| `benefits/_booking_voucher.html` | 22 |
| `partner_admin/_edit_modal.html` | 70, 93 (uses `/static/{{ ... }}`) |

Also check `partner_admin/_add_modal.html` and `partners/_grid.html`. `_grid.html` uses
`{{ p.logo_image }}` raw, so confirm what that page expects (it may be dead code from the old
`/partners` router).

Example:

```jinja
{# before #}
src="{{ url_for('static', path=p.logo_image) if p.logo_image else 'https://placehold.co/...' }}"
{# after #}
src="{{ media_url(p.logo_image) if p.logo_image else 'https://placehold.co/...' }}"
```

### 3.6 Scripts

- `scripts/resize_partner_images.py` works on the local folder. Either run it before the
  `upload-batch` in 2.2, or adapt it to download, resize and re-upload blobs.
- `scripts/sync_dev_to_qa_partners.sql` copies partner rows between environments. After it runs,
  copy the matching blobs too:
  ```bash
  az storage blob copy start-batch \
    --account-name gor2026media \
    --source-container gor-qa --destination-container gor-prod \
    --pattern "partners/*" --auth-mode login
  ```

### 3.7 `.gitignore`

Change `/app/static/` to `/app/static/partners/`, then commit the design assets
(`v2/`, `fonts/`, logos, icons) so they're version-controlled again.

---

## Part 4 — Rollout order

1. **Part 1** Azure setup, without `MEDIA_BASE_URL` yet.
2. **Part 2.1** rescue server-only images.
3. **Part 2.2** upload to both containers.
4. **Part 3** code changes, tested locally with and without the env vars.
5. Deploy to QA. With `MEDIA_BASE_URL` still unset it behaves exactly as today.
6. Set `MEDIA_BASE_URL` on `gor26-Q` (setting changes restart the app).
7. Test on QA:
   - Partner list, partner detail and voucher pages show images (DevTools → image URLs point at `blob.core.windows.net`).
   - Upload a new logo in partner admin → it appears straight away and is in the `gor-qa` container.
   - Redeploy QA → the uploaded logo is still there. **This is the test that matters.**
8. Repeat steps 5–7 for prod (`gor26-P`).

**Rollback:** delete the `MEDIA_BASE_URL` app setting. The app goes back to `/static/` straight
away, with no redeploy.

---

## Cost

About 30 MB of storage plus egress for partner images. Expect well under $1/month on Standard LRS.
