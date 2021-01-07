#!/usr/bin/env sh
set -e

npm run build
zip -rq dist/dist.zip dist/

cd dist
#echo 'https://kwic.netlify.com/* https://kwic.yongfu.name/:splat 301!' > _redirects

git init
git add -A
git commit -m 'deploy'
git push -f https://github.com/liao961120/concordancer.git master:query-interface

cd -
