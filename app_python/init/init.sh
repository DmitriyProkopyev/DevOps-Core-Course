set -e
echo "Downloading file..."

mkdir -p /shared
curl --no-verbose -L -o /shared/lab16.md \
  https://raw.githubusercontent.com/DmitriyProkopyev/DevOps-Core-Course/master/labs/lab16.md

echo "File saved to /shared/labs16.md:"
head /shared/lab16.md
echo "..."
