#! /bin/bash
sudo rm -fr madesoft2
git clone https://github.com/jandresh/madesoft2
cd madesoft2/
for branch in `git branch -r | grep -v HEAD`;do echo -e `git show --format="%ci" $branch | head -n 1` \\t$branch; done | sort -r | head -n 1 | grep -o -P '(?<=origin/).*(?=)' > branch.txt
export LAST_BRANCH=$(cat branch.txt)
git checkout $LAST_BRANCH
cd orchestratorws/kompose
sudo docker-compose down --remove-orphans
cd ../../dbws/kompose
sudo docker-compose down --remove-orphans
cd ../../preprocessingws/kompose
sudo docker-compose down --remove-orphans
cd ../../corews/kompose
sudo docker-compose down --remove-orphans
cd ../../metapubws/kompose
sudo docker-compose down --remove-orphans
cd ..
sudo docker-compose build
sudo docker-compose up -d
cd ../corews
sudo docker-compose build
sudo docker-compose up -d
cd ../preprocessingws
sudo docker-compose build
sudo docker-compose up -d
cd ../dbws
sudo docker-compose build
sudo docker-compose up -d
cd ../orchestratorws
sudo docker-compose build
sudo docker-compose up -d
