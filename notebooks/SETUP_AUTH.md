# Authentication Setup for Fantasy Football Notebooks

## Quick Fix for the Authentication Error

Your `.env` file needs the following variables set correctly:

### 1. Check Your `.env` File

Make sure your `.env` file in the project root has these variables:

```bash
# Cognite Data Fusion Configuration
CDF_PROJECT=sofie-prod
CDF_CLUSTER=bluefield
CDF_BASE_URL=https://bluefield.cognitedata.com

# Azure AD OAuth credentials
CDF_TOKEN_URL=https://login.microsoftonline.com/YOUR-TENANT-ID/oauth2/v2.0/token
CDF_CLIENT_ID=YOUR-CLIENT-ID
CDF_CLIENT_SECRET=YOUR-CLIENT-SECRET

# Fantasy Premier League
FPL_LEAGUE_ID=sl9tyc
```

### 2. Get Your Credentials

You need three pieces of information from your Azure AD app registration:

1. **Tenant ID** - Your Azure tenant identifier
2. **Client ID** - Your app's client/application ID
3. **Client Secret** - Your app's client secret value

### 3. Where to Find These Values

#### Option A: Ask Your CDF Admin
Contact your CDF project administrator for these credentials.

#### Option B: Azure Portal (if you have access)
1. Go to https://portal.azure.com
2. Navigate to **Azure Active Directory** → **App registrations**
3. Find your app (or create a new one)
4. **Tenant ID**: Found in the app Overview
5. **Client ID**: Also in the Overview (Application ID)
6. **Client Secret**: Under **Certificates & secrets** → Create a new client secret

### 4. Update Your `.env` File

Replace the placeholder values:

```bash
# Before:
CDF_TOKEN_URL=https://login.microsoftonline.com/YOUR-TENANT-ID/oauth2/v2.0/token
CDF_CLIENT_ID=YOUR-CLIENT-ID
CDF_CLIENT_SECRET=YOUR-CLIENT-SECRET

# After (example):
CDF_TOKEN_URL=https://login.microsoftonline.com/12345678-1234-1234-1234-123456789012/oauth2/v2.0/token
CDF_CLIENT_ID=abcdef12-3456-7890-abcd-ef1234567890
CDF_CLIENT_SECRET=your-secret-value-here
```

### 5. Test the Connection

Restart your Jupyter kernel and run the first cell again. You should see:

```
Connecting to CDF...
✓ Connected to project: sofie-prod
✓ Cluster: bluefield
✓ FPL API client initialized
```

## Troubleshooting

### Error: "Missing required environment variables"
- Make sure your `.env` file is in the project root directory
- Check that variable names match exactly (case-sensitive)
- No spaces around the `=` sign

### Error: "invalid_client" or "unauthorized_client"
- Double-check your CLIENT_ID and CLIENT_SECRET
- Verify the TOKEN_URL has the correct tenant ID
- Make sure your app has permissions for CDF

### Error: "invalid_scope"
- Check that CDF_BASE_URL matches your cluster
- Verify the scope format: `https://bluefield.cognitedata.com/.default`

## Security Note

⚠️ **Never commit your `.env` file to git!**

The `.env` file is already in `.gitignore` to prevent accidental commits.

