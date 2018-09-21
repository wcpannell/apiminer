#!/usr/bin/env bash
# push sphinx HTML to gh-pages
set -e

cd ..
git clone -b gh-pages "https://$GH_TOKEN@github.com/wcpannell/apiminer.git" gh-pages
cd gh-pages

if [ "$1" != "dry" ]; then
	git config user.name "Travis Builder"
	git config user.email "2120605+wcpannell@users.noreply.github.com"
fi

cp -R ../$REPO/docs/_build/html/* ./
git add -A .
git commit -m "[ci skip] Autodoc commit for $COMMIT."
if [ "$1" != "dry" ]; then
	git push -q origin gh-pages
	# -q prevents leaking token
fi
