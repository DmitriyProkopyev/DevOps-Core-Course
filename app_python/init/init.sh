set -e
echo "Downloading file..."

mkdir -p /app/shared
curl --no-verbose -L -o /app/shared/lab16.md \
  https://raw.githubusercontent.com/DmitriyProkopyev/DevOps-Core-Course/master/labs/lab16.md

echo "File saved to /app/shared/labs16.md:"
head /app/shared/lab16.md
echo "..."
