#! /bin/bash
sudo rm -fr inv-adc
git clone https://github.com/jandresh/inv-adc
cd inv-adc/
for branch in `git branch -r | grep -v HEAD`;do echo -e `git show --format="%ci" $branch | head -n 1` \\t$branch; done | sort -r | head -n 1 | grep -o -P '(?<=origin/).*(?=)' > branch.txt
export LAST_BRANCH=$(cat branch.txt)
git checkout $LAST_BRANCH
cd adcws/mysqlws
sudo docker-compose down
cd ../metapubws
sudo docker-compose down
cd kompose
sudo docker-compose up -d
cd ../../mysqlws
sudo docker-compose down
cd kompose
sudo docker-compose up -d

# sudo rm -fr ontop-tutorial
# git clone https://github.com/ontop/ontop-tutorial.git
# cd ontop-tutorial/endpoint
# sudo docker-compose build
# sudo docker-compose up -d