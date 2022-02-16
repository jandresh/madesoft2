agentName = "ubuntu-2110"
agentLabel = "${-> println 'Right Now the Agent Name is ' + agentName; return agentName}"
pipeline {
    environment {
        PROJECT = "madesoft2"
        APP_NAME = "madesoft2-app"
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
                sh 'chmod 777 test-environment1.sh'
                sh 'sh test-environment1.sh'
            }
        }
        stage('Container Publish') {
            agent {
                node { label agentLabel as String }
            }
            steps {
                echo "Container push to DockerHub"
                sh 'chmod 777 container-publish.sh'
                sh 'sh container-publish.sh'
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
                sh 'chmod 777 test-environment2.sh'
                sh 'sh test-environment2.sh'
                sh 'sh functional.sh'
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
                    label 'madesoft2-app'
                    defaultContainer 'jnlp'
                    yamlFile 'pod-template.yaml'
                }
            }
            steps {
                container('kubectl') {
                    sh("kubectl get ns ${env.BRANCH_NAME} || kubectl create ns ${env.BRANCH_NAME}")
                    sh("sed -i.bak 's#jandresh/metapubws:latest#jandresh/metapubws:${IMAGE_TAG}#' ./metapubws/kube/dev/*.yaml")
                    sh("sed -i.bak 's#jandresh/corews:latest#jandresh/corews:${IMAGE_TAG}#' ./corews/kube/dev/*.yaml")
                    sh("sed -i.bak 's#jandresh/preprocessingws:latest#jandresh/preprocessingws:${IMAGE_TAG}#' ./preprocessingws/kube/dev/*.yaml")
                    sh("sed -i.bak 's#jandresh/dbws:latest#jandresh/dbws:${IMAGE_TAG}#' ./dbws/kube/dev/*.yaml")
                    sh("sed -i.bak 's#jandresh/orchestratorws:latest#jandresh/orchestratorws:${IMAGE_TAG}#' ./orchestratorws/kube/dev/*.yaml")
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'metapubws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'metapubws/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'corews/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'corews/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'preprocessingws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'preprocessingws/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'dbws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'dbws/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'orchestratorws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'orchestratorws/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment metapubws --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment corews --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment preprocessingws --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment dbws --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment mysql --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment mongo --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment orchestratorws --replicas=1")
                    sh("echo http://`kubectl --namespace=${env.BRANCH_NAME} get service/orchestratorws -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`:5004 > url")
                    sh("echo http://`kubectl --namespace=${env.BRANCH_NAME} get service/dbws -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`:5001 > url")
                }
            }
        }
        stage('Deploy Canary') {
            // Canary branch
            when { branch 'canary' }
            agent {
                kubernetes {
                    label 'madesoft2-app'
                    defaultContainer 'jnlp'
                    yamlFile 'pod-template.yaml'
                }
            }
            steps {
                container('kubectl') {
                    sh("kubectl get ns production || kubectl create ns production")
                    sh("sed -i.bak 's#jandresh/metapubws:latest#jandresh/metapubws:${IMAGE_TAG}#' ./metapubws/kube/canary/*.yaml")
                    sh("sed -i.bak 's#jandresh/corews:latest#jandresh/corews:${IMAGE_TAG}#' ./corews/kube/canary/*.yaml")
                    sh("sed -i.bak 's#jandresh/preprocessingws:latest#jandresh/preprocessingws:${IMAGE_TAG}#' ./preprocessingws/kube/canary/*.yaml")
                    sh("sed -i.bak 's#jandresh/dbws:latest#jandresh/dbws:${IMAGE_TAG}#' ./dbws/kube/canary/*.yaml")
                    sh("sed -i.bak 's#jandresh/orchestratorws:latest#jandresh/orchestratorws:${IMAGE_TAG}#' ./orchestratorws/kube/canary/*.yaml")
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'metapubws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'metapubws/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'corews/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'corews/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'preprocessingws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'preprocessingws/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'dbws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'dbws/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'orchestratorws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'orchestratorws/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    sh("kubectl --namespace=production scale deployment metapubws --replicas=1")
                    sh("kubectl --namespace=production scale deployment corews --replicas=1")
                    sh("kubectl --namespace=production scale deployment preprocessingws --replicas=1")
                    sh("kubectl --namespace=production scale deployment dbws --replicas=1")
                    sh("kubectl --namespace=production scale deployment mysql --replicas=1")
                    sh("kubectl --namespace=production scale deployment mongo --replicas=1")
                    sh("kubectl --namespace=production scale deployment orchestratorws --replicas=1")
                    sh("echo http://`kubectl --namespace=production get service/orchestratorws -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`:5004 > url")
                    sh("echo http://`kubectl --namespace=production get service/dbws -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`:5001 > url")
                }
            }
        }
        stage('Deploy Production') {
            // Production branch
            when { branch 'master' }
            agent {
                kubernetes {
                    label 'madesoft2-app'
                    defaultContainer 'jnlp'
                    yamlFile 'pod-template.yaml'
                }
            }
            steps{
                container('kubectl') {
                    sh("kubectl get ns production || kubectl create ns production")
                    sh("sed -i.bak 's#jandresh/metapubws:latest#jandresh/metapubws:${IMAGE_TAG}#' ./metapubws/kube/production/*.yaml")
                    sh("sed -i.bak 's#jandresh/corews:latest#jandresh/corews:${IMAGE_TAG}#' ./corews/kube/production/*.yaml")
                    sh("sed -i.bak 's#jandresh/preprocessingws:latest#jandresh/preprocessingws:${IMAGE_TAG}#' ./preprocessingws/kube/production/*.yaml")
                    sh("sed -i.bak 's#jandresh/dbws:latest#jandresh/dbws:${IMAGE_TAG}#' ./dbws/kube/production/*.yaml")
                    sh("sed -i.bak 's#jandresh/orchestratorws:latest#jandresh/orchestratorws:${IMAGE_TAG}#' ./orchestratorws/kube/production/*.yaml")
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'metapubws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'metapubws/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'corews/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'corews/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'preprocessingws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'preprocessingws/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'dbws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'dbws/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'orchestratorws/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'orchestratorws/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    sh("kubectl --namespace=production scale deployment metapubws --replicas=3")
                    sh("kubectl --namespace=production scale deployment corews --replicas=3")
                    sh("kubectl --namespace=production scale deployment preprocessingws --replicas=3")
                    sh("kubectl --namespace=production scale deployment dbws --replicas=3")
                    sh("kubectl --namespace=production scale deployment mysql --replicas=1")
                    sh("kubectl --namespace=production scale deployment mongo --replicas=1")
                    sh("kubectl --namespace=production scale deployment orchestratorws --replicas=3")
                    sh("echo http://`kubectl --namespace=production get service/orchestratorws -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`:5004 > url")
                    sh("echo http://`kubectl --namespace=production get service/dbws -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`:5001 > url")
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
