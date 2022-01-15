agentName = "ubuntu-2104"
agentLabel = "${-> println 'Right Now the Agent Name is ' + agentName; return agentName}"
pipeline {
    environment {
        PROJECT = "compdistuv"
        APP_NAME = "compdistuv-app"
        FE_SVC_NAME = "metapub"
        CLUSTER = "jenkins-cd"
        CLUSTER_ZONE = "us-east1-d"
        JENKINS_CRED = "${PROJECT}"
        IMAGE_TAG = "${env.GIT_COMMIT}"
    }
    agent none
    stages {
        stage('Build&Test app') {
            agent { 
                node { label agentLabel as String }
            }
            steps {
                echo "Deployment test environment from docker-compose.yml"
                sh 'chmod 777 adcws/test-environment1.sh'
                sh 'sh adcws/test-environment1.sh'
            }
        }
        stage('Container Publish') {
            agent { 
                node { label agentLabel as String }
            }
            steps {
                echo "Container push to DockerHub"
                sh 'chmod 777 adcws/container-publish.sh'
                sh 'sh adcws/container-publish.sh'
                script {
                    IMAGE_TAG=sh (
                        script: 'echo -n $GIT_COMMIT',
                        returnStdout: true
                    )
                }             
            }
        }
        stage('Test App form dockerHub') {
            agent { 
                node { label agentLabel as String }
            }
            steps {
                echo "Deployment test environment from docker hub"
                sh 'chmod 777 adcws/test-environment2.sh'
                sh 'sh adcws/test-environment2.sh'
            }
        }
        stage('Deploy Developer') {
            // Developer Branches
            when {
                not { branch 'master' }
                not { branch 'canary' }
            }
            agent {
                kubernetes {
                    label 'compdistuv-app'
                    defaultContainer 'jnlp'
                    yamlFile 'adcws/pod-template.yaml'
                }
            }
            steps {
                container('kubectl') {
                    // Create namespace if it doesn't exist
                    sh("kubectl get ns ${env.BRANCH_NAME} || kubectl create ns ${env.BRANCH_NAME}")
                    // sh("gcloud compute disks create --size=20GB --zone=us-east1-d my-db-${env.BRANCH_NAME} || gcloud compute disks describe my-db-${env.BRANCH_NAME} --zone us-east1-d")                    
                    sh("sed -i.bak 's#jandresh/metapubws:latest#jandresh/metapubws:${IMAGE_TAG}#' ./adcws/metapubws/kube/dev/*.yaml")
                    sh("sed -i.bak 's#jandresh/mysqlws:latest#jandresh/mysqlws:${IMAGE_TAG}#' ./adcws/mysqlws/kube/dev/*.yaml")
                    sh("sed -i.bak 's#my-db-production#my-db-${env.BRANCH_NAME}#' ./adcws/mysqlws/kube/services/*.yaml")
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'adcws/metapubws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'adcws/metapubws/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'adcws/mysqlws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'adcws/mysqlws/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment metapubws --replicas=4")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment app --replicas=4")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment db --replicas=1")
                    sh("echo http://`kubectl --namespace=${env.BRANCH_NAME} get service/${FE_SVC_NAME} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'` > ${FE_SVC_NAME}:3000")
                }
            }
        }  
        stage('Deploy Canary') {
            // Canary branch
            when { branch 'canary' }
            agent {
                kubernetes {
                    label 'compdistuv-app'
                    defaultContainer 'jnlp'
                    yamlFile 'adcws/pod-template.yaml'
                }
            }
            steps {
                container('kubectl') {
                    // Create namespace if it doesn't exist
                    sh("kubectl get ns production || kubectl create ns production")
                    sh("sed -i.bak 's#jandresh/metapubws:latest#jandresh/metapubws:${IMAGE_TAG}#' ./adcws/metapubws/kube/canary/*.yaml")
                    sh("sed -i.bak 's#jandresh/mysqlws:latest#jandresh/mysqlws:${IMAGE_TAG}#' ./adcws/mysqlws/kube/canary/*.yaml")
                    // sh("gcloud compute disks create --size=20GB --zone=us-east1-d my-db-production || gcloud compute disks describe my-db-production --zone us-east1-d") 
                    step([$class: 'KubernetesEngineBuilder', namespace:'production', projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'adcws/metapubws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace:'production', projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'adcws/metapubws/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace:'production', projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'adcws/mysqlws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace:'production', projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'adcws/mysqlws/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    // sh("kubectl --namespace=production scale deployment blog --replicas=1")
                    // sh("kubectl --namespace=production scale deployment app --replicas=1")
                    // sh("kubectl --namespace=production scale deployment db --replicas=1")
                    sh("echo http://`kubectl --namespace=production get service/${FE_SVC_NAME} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'` > ${FE_SVC_NAME}:3000")
                }
            }
        }
        stage('Deploy Production') {
            // Production branch
            when { branch 'master' }
            agent {
                kubernetes {
                    label 'compdistuv-app'
                    defaultContainer 'jnlp'
                    yamlFile 'adcws/pod-template.yaml'
                }
            }
            steps{
                container('kubectl') {
                    // Create namespace if it doesn't exist
                    sh("kubectl get ns production || kubectl create ns production")
                    sh("sed -i.bak 's#jandresh/metapubws:latest#jandresh/metapubws:${IMAGE_TAG}#' ./adcws/metapubws/kube/production/*.yaml")
                    sh("sed -i.bak 's#jandresh/mysqlws:latest#jandresh/mysqlws:${IMAGE_TAG}#' ./adcws/mysqlws/kube/production/*.yaml")
                    // sh("gcloud compute disks create --size=20GB --zone=us-east1-d my-db-production || gcloud compute disks describe my-db-production --zone us-east1-d") 
                    step([$class: 'KubernetesEngineBuilder', namespace:'production', projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'adcws/metapubws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace:'production', projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'adcws/metapubws/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace:'production', projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'adcws/mysqlws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace:'production', projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'adcws/mysqlws/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    sh("kubectl --namespace=production scale deployment metapubws --replicas=4")
                    sh("kubectl --namespace=production scale deployment app --replicas=4")
                    sh("kubectl --namespace=production scale deployment db --replicas=1")
                    sh("echo http://`kubectl --namespace=production get service/${FE_SVC_NAME} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'` > ${FE_SVC_NAME}:3000")
                }
            }
        }    
    }
    post {
        always {
            echo 'This will always run'
        }
        success {
            echo 'This will run only if successful'
        }
        failure {
            echo 'This will run only if failed'
        }
        unstable {
            echo 'This will run only if the run was marked as unstable'
        }
        changed {
            echo 'This will run only if the state of the Pipeline has changed'
            echo 'For example, if the Pipeline was previously failing but is now successful'
        }
    }
}