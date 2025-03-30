#!/bin/bash

# Create DOCUMENT_ROOT tree
mkdir -p www_root/{public,private,images,assets/js} www_root/"dir with spaces"

# 1. Standard files
cat <<EOF > www_root/index.html
<!DOCTYPE html>
<html>
<head><title>Test Server</title></head>
<body><h1>It works!</h1></body>
</html>
EOF
echo "Plain text file" > www_root/file.txt
echo "Secret data" > www_root/private/secret.txt

# 2. Files with spaces and special symbols
echo "Spaced file" > "www_root/file with spaces.txt"
echo "Cyrillic тест" > "www_root/русский_файл.txt"

# 3. Binary files (1MB and 5MB)
dd if=/dev/urandom of=www_root/images/random.jpg bs=1M count=1
truncate -s 5M www_root/assets/large.bin

# 4. Directory with index.html
echo "<h1>Public</h1>" > www_root/public/index.html
echo "<h1>Spaced Dir</h1>" > "www_root/dir with spaces/index.html"

# 5. Test js/css files
echo "function test(){ return 42; }" > www_root/assets/js/app.js
echo "body { background: #fff; }" > www_root/assets/style.css

# 6. Symbolic link (if supported)
ln -s ../file.txt www_root/public/link.txt
