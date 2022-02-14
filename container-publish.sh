#! /bin/bash
sudo rm -fr madesoft2
git clone https://github.com/jandresh/madesoft2
cd madesoft2
for branch in `git branch -r | grep -v HEAD`;do echo -e `git show --format="%ci" $branch | head -n 1` \\t$branch; done | sort -r | head -n 1 | grep -o -P '(?<=origin/).*(?=)' > branch.txt
export LAST_BRANCH=$(cat branch.txt)
git checkout $LAST_BRANCH
sudo docker login -u="jandresh" -p="cb64422a-f28c-4ee7-b717-f605e309a1b2"
cd metapubws
sudo docker build -t jandresh/metapubws:$GIT_COMMIT .
sudo docker push jandresh/metapubws:$GIT_COMMIT
sudo docker build -t jandresh/metapubws:latest .
sudo docker push jandresh/metapubws:latest
cd ../corews/app
sudo docker build -t jandresh/corews:$GIT_COMMIT .
sudo docker push jandresh/corews:$GIT_COMMIT
sudo docker build -t jandresh/corews:latest .
sudo docker push jandresh/corews:latest
cd ../../preprocessingws/app
sudo docker build -t jandresh/preprocessingws:$GIT_COMMIT .
sudo docker push jandresh/preprocessingws:$GIT_COMMIT
sudo docker build -t jandresh/preprocessingws:latest .
sudo docker push jandresh/preprocessingws:latest
cd ../../dbws/app
sudo docker build -t jandresh/dbws:$GIT_COMMIT .
sudo docker push jandresh/dbws:$GIT_COMMIT
sudo docker build -t jandresh/dbws:latest .
sudo docker push jandresh/dbws:latest
cd ../../orchestratorws/app
sudo docker build -t jandresh/orchestratorws:$GIT_COMMIT .
sudo docker push jandresh/orchestratorws:$GIT_COMMIT
sudo docker build -t jandresh/orchestratorws:latest .
sudo docker push jandresh/orchestratorws:latest
