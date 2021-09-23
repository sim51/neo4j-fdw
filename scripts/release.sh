#!/bin/bash

###############################################################################
#
# = Release script for the project
#
# == Requirements
#  - jq
#  - git
#  - github-release-cli (https://www.npmjs.com/package/github-release-cli)
###############################################################################
version=$(grep default_version ./neo4j-fdw.control | sed -e "s/default_version[[:space:]]*=[[:space:]]*'\([^']*\)'/\1/" | sed "s/-dev//")
echo "Release version is $version"
next_version=""
read -e -p "What is the next version : " -i "$next_version" next_version

git update-index -q --refresh
CHANGED=$(git diff-index --name-only HEAD --)
if [ ! -z "$CHANGED" ]; then
  echo "You have some local changes"
  echo "$(git status)"
  exit 1
fi

echo "Pushing"
git push


echo "~ Generate the project archive"
git archive --format zip --prefix=neo4j-fdw_v$version/ --output ./neo4j-fdw_v$version.zip HEAD
unzip ./neo4j-fdw_v$version.zip
rm ./neo4j-fdw_v$version.zip
sed -i -e "s/__VERSION__/$version/g" ./neo4j-fdw_v$version/META.json ./neo4j-fdw_v$version/neo4j-fdw.control ./neo4j-fdw_v$version/setup.py ./neo4j-fdw_v$version/neo4jPg/__init__.py
zip -r ./neo4j-fdw_v$version.zip ./neo4j-fdw_v$version/
rm -rf neo4j-fdw_v$version/

echo "~ Generate release notes"

tmpfile=$(mktemp /tmp/release-neo4j-fdw.XXXXXX)
echo "# Neo4j FDW Release v$version" > "$tmpfile"

# retrieve last tag if not set
latest=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/sim51/neo4j-fdw/tags" | jq -r '.[0].commit.sha')
echo "" >> "$tmpfile"
echo "## Commits" >> "$tmpfile"
echo "" >> "$tmpfile"
if [[ $latest == 'null'  ]]; then
  git log HEAD --oneline >> "$tmpfile"
else
  git log "$latest"..HEAD --oneline >> "$tmpfile"
fi


# Create the github release notes
# based on https://www.npmjs.com/package/github-release-cli
echo "Running github release github-release"
github-release upload  --owner=sim51  --repo=neo4j-fdw  --tag="v$version"  --release-name="v$version"  --body="$(cat $tmpfile)"  neo4j-fdw_v$version.zip

echo "Go to next version for dev"
cat ./neo4j-fdw.control | sed -e "s/default_version[[:space:]]*=[[:space:]]*'\([^']*\)'/default_version = '${next_version}-dev'/" > ./neo4j-fdw.control.new
rm ./neo4j-fdw.control
mv ./neo4j-fdw.control.new  ./neo4j-fdw.control

echo "Don't forget to upload the zip file at https://manager.pgxn.org/upload"
