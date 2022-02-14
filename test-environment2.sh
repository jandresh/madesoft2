#! /bin/bash
sudo rm -fr madesoft2
git clone https://github.com/jandresh/madesoft2
cd madesoft2
for branch in `git branch -r | grep -v HEAD`;do echo -e `git show --format="%ci" $branch | head -n 1` \\t$branch; done | sort -r | head -n 1 | grep -o -P '(?<=origin/).*(?=)' > branch.txt
export LAST_BRANCH=$(cat branch.txt)
git checkout $LAST_BRANCH
cd orchestratorws
sudo docker-compose down --remove-orphans
cd ../dbws
sudo docker-compose down --remove-orphans
cd ../preprocessingws
sudo docker-compose down --remove-orphans
cd ../corews
sudo docker-compose down --remove-orphans
cd ../metapubws
sudo docker-compose down --remove-orphans
cd kompose
sudo docker-compose up -d
cd ../../corews/kompose
sudo docker-compose up -d
cd ../../preprocessingws/kompose
sudo docker-compose up -d
cd ../../dbws/kompose
sudo docker-compose up -d
cd ../../orchestratorws/kompose
sudo docker-compose up -d
