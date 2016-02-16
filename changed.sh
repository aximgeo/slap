git diff --name-only HEAD~1 | grep -i \.mxd | sed -e 's/^/-i /'
