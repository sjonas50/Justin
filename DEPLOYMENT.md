# Deployment Guide for Vercel

## Database Setup

This application now supports both SQLite (for local development) and PostgreSQL (for production on Vercel).

### Local Development
- The app will automatically use SQLite when no `DATABASE_URL` is set
- Data is stored in `stock_database.db` and `user_profiles.db`

### Production (Vercel)
1. **Create a PostgreSQL Database**:
   - Go to your Vercel dashboard
   - Navigate to the Storage tab
   - Create a new PostgreSQL database
   - Copy the connection string

2. **Set Environment Variables in Vercel**:
   ```
   DATABASE_URL=<your-postgresql-connection-string>
   ANTHROPIC_API_KEY=<your-anthropic-api-key>
   SECRET_KEY=<generate-a-secure-secret-key>
   FLASK_ENV=production
   ```

3. **Deploy to Vercel**:
   ```bash
   # Install Vercel CLI if you haven't
   npm i -g vercel

   # Deploy
   vercel
   ```

## Migration from SQLite to PostgreSQL

If you have existing data in SQLite that you want to migrate:

1. Set your `DATABASE_URL` environment variable locally
2. Run the migration script:
   ```bash
   python migrate_db.py
   ```

## Important Notes

- The app automatically creates database tables on startup
- Logging is configured for console output (compatible with Vercel)
- The database manager automatically detects whether to use SQLite or PostgreSQL based on the `DATABASE_URL` environment variable

## Troubleshooting

- If you see database connection errors, check your `DATABASE_URL` format
- Vercel PostgreSQL URLs sometimes start with `postgres://` - the app automatically converts this to `postgresql://`
- Check Vercel logs for any startup errors