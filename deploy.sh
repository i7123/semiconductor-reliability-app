#!/bin/bash

echo "🚀 Deploying Semiconductor Reliability Calculator to Vercel..."
echo "============================================================="

# Check if user is logged in to Vercel
if ! vercel whoami > /dev/null 2>&1; then
    echo "❌ Not logged in to Vercel. Please run: vercel login"
    exit 1
fi

echo "✅ Vercel authentication confirmed"

# Deploy to production
echo "🚀 Deploying to production..."
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your app should now be available at:"
echo "   https://semiconductor-reliability-calculator.vercel.app"
echo ""
echo "📋 Next steps:"
echo "   1. Set environment variables in Vercel dashboard"
echo "   2. Test all calculator functions"
echo "   3. Share the URL with users!"
echo ""
echo "📖 For detailed instructions, see: VERCEL_DEPLOY.md"