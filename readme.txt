# how to push files to Google Apps Studio
# clasp configuration is in .clasp.json and .claspignore
> clasp push

# how to push client.js to unpkg
# 1. Ensure client.js is part of a public npm package.
# 2. Update the package version in package.json.
# 3. Publish the package to npm:
> npm publish
# 4. Access the file via unpkg:
#    https://unpkg.com/<package-name>@<version>/client.js
