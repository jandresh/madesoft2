#! /bin/bash
sudo rm -fr madesoft2
git clone https://github.com/jandresh/madesoft2
cd madesoft2/
for branch in `git branch -r | grep -v HEAD`;do echo -e `git show --format="%ci" $branch | head -n 1` \\t$branch; done | sort -r | head -n 1 | grep -o -P '(?<=origin/).*(?=)' > branch.txt
export LAST_BRANCH=$(cat branch.txt)
git checkout development
git merge $LAST_BRANCH
git branch -d $LAST_BRANCH
# git push
