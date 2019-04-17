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
git archive --format zip --prefix=neo4j-fdw_v$1/ --output ./neo4j-fdw_v$1.zip HEAD
unzip ./neo4j-fdw_v$1.zip
rm ./neo4j-fdw_v$1.zip
sed -i -e "s/@@VERSION@@/$1/g" ./neo4j-fdw_v$1/META.json ./neo4j-fdw_v$1/setup.py ./neo4j-fdw_v$1/neo4jPg/__init__.py
zip -r ./neo4j-fdw_v$1.zip ./neo4j-fdw_v$1/
rm -rf neo4j-fdw_v$1/

echo "~ Generate release notes"

tmpfile=$(mktemp /tmp/release-neo4j-fdw.XXXXXX)
echo "# Neo4j FDW Release v$1" > "$tmpfile"

echo "Retrieving milestone issues"
status=$(curl -w "%{http_code}" -s -o /dev/null -I -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/sim51/neo4j-fdw/issues?milestone=v$1")
if [[ status == '200' ]]; then

  echo "" >> "$tmpfile"
  echo "## Fixes" >> "$tmpfile"
  echo "" >> "$tmpfile"
  curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/sim51/neo4j-fdw/issues?milestone=v$1&state=closed&sort=updated&labels=bug" | jq -r '.[] | [(.number), .title] | @tsv' | sed s/^/#/g >> "$tmpfile"

  echo "" >> "$tmpfile"
  echo "## Improvements" >> "$tmpfile"
  echo "" >> "$tmpfile"
  curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/sim51/neo4j-fdw/issues?milestone=v$1&state=closed&sort=updated&labels=enhancement" | jq -r '.[] | [(.number), .title] | @tsv' | sed s/^/#/g >> "$tmpfile"
fi

# retrieve last tag if not set
latest=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/sim51/neo4j-fdw/tags" | jq -r '.[0].name')
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
github-release upload  --owner=sim51  --repo=neo4j-fdw  --tag="v$1"  --name="v$1"  --body="$(cat $tmpfile)"  neo4j-fdw_v$1.zip

echo "Don't forget to upload the zip file at https://manager.pgxn.org/upload"