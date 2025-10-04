### Managing Root Folders in Collections
 
 1. Go to the Collections Manager page
 2. Select a collection by clicking the select button (checkmark icon)
 3. In the Root Folders section:
    - **To link a new root folder**: Click "Link Root Folder" button
    - Select an available root folder from the dropdown
    - Click "Link" to confirm
    - Only root folders not already linked to this collection will be shown
 
 Alternatively, you can create a new root folder and add it to the selected collection:
 
### Removing Root Folders from a Collection
 
 1. Go to the Collections Manager page
 2. Select a collection
 3. In the Root Folders section, find the root folder to remove
 4. Click the remove button (unlink icon)
 5. Confirm the removal
 
### Removing Series from a Collection
 
## Troubleshooting
 
### Link Root Folder Button Not Working

If the "Link Root Folder" button doesn't respond:
1. Ensure you've selected a collection first (click the eye icon)
2. Check browser console for JavaScript errors
3. Verify the API endpoints are accessible:
   - `GET /api/root-folders`
   - `GET /api/collections/{id}/root-folders`
   - `POST /api/collections/{id}/root-folders/{folder_id}`
4. Hard refresh the page (Ctrl+F5) to ensure latest JavaScript is loaded

### Collection Not Showing Series

If a series isn't showing up in a collection:
