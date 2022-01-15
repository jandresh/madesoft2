#! /bin/bash
sudo rm -fr inv-adc
git clone https://github.com/jandresh/inv-adc
cd inv-adc/adcws/metapubws
for branch in `git branch -r | grep -v HEAD`;do echo -e `git show --format="%ci" $branch | head -n 1` \\t$branch; done | sort -r | head -n 1 | grep -o -P '(?<=origin/).*(?=)' > branch.txt
export LAST_BRANCH=$(cat branch.txt)
git checkout $LAST_BRANCH
sudo docker login -u="jandresh" -p="cb64422a-f28c-4ee7-b717-f605e309a1b2"
sudo docker build -t jandresh/metapubws:$GIT_COMMIT .
sudo docker push jandresh/metapubws:$GIT_COMMIT
sudo docker build -t jandresh/metapubws:latest .
sudo docker push jandresh/metapubws:latest
cd ../mysqlws/app
sudo docker build -t jandresh/mysqlws:$GIT_COMMIT .
sudo docker push jandresh/mysqlws:$GIT_COMMIT
sudo docker build -t jandresh/mysqlws:latest .
sudo docker push jandresh/mysqlws:latest