# Firebase Setup for Community Voting

## 1. Create Firebase Project

1. Go to https://console.firebase.google.com/
2. Click **"Add project"** → name it `turkey-repeaters`
3. Disable Google Analytics (not needed) → **Create project**

## 2. Enable Anonymous Authentication

1. In Firebase Console → **Authentication** → **Sign-in method**
2. Enable **Anonymous** → Save

## 3. Create Firestore Database

1. Firebase Console → **Firestore Database** → **Create database**
2. Select **production mode**
3. Choose a location (e.g., `europe-west1` for Turkey)
4. After creation, go to **Rules** tab
5. Replace rules with the contents of `firestore.rules` from this repo
6. **Publish** the rules

## 4. Create Initial Aggregate Document

1. In Firestore Console → **Start collection**: `aggregates`
2. Add document with ID: `votes`
3. Add a dummy field (e.g., `_init: true`) — it will be populated as users vote

## 5. Get Firebase Config

1. Firebase Console → Project Settings (gear icon) → **General**
2. Under "Your apps" → Click **Web** icon (`</>`)
3. Register app name: `turkey-repeaters-web`
4. Copy the `firebaseConfig` object values
5. Update `docs/index.html` — find `FIREBASE_CONFIG` and replace:
   - `apiKey` → your API key
   - `authDomain` → `turkey-repeaters.firebaseapp.com`
   - `projectId` → `turkey-repeaters`
   - `storageBucket` → your storage bucket
   - `messagingSenderId` → your sender ID
   - `appId` → your app ID

## 6. Deploy

```bash
git add -A && git commit -m "Add Firebase config" && git push
```

GitHub Pages will update automatically within a few minutes.

## Security Notes

- Anonymous auth means no login required — each browser gets a unique ID
- Users can vote once per repeater (changing vote adjusts counts)
- Firestore rules ensure users can only modify their own vote records
- The API key is safe to expose — Firestore rules handle authorization
