#!/bin/bash

# Reset the bot (delete all data)

echo "⚠️  This will delete all bot data!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    echo "Stopping bot..."
    docker-compose down -v
    echo "✅ Data cleared"
else
    echo "Cancelled"
fi
