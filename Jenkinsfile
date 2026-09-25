pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'python3 -m venv .venv'
                sh '.venv/bin/pip install -r requirements.txt'
            }
        }

        stage('Initialize Database') {
            steps {
                sh '.venv/bin/python scripts/seed.py'
            }
        }

        stage('Run Tests') {
            steps {
                sh '.venv/bin/pytest -q'
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )]) {
                        sh '''
                            echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
                            docker build -t devopsmart:${BUILD_NUMBER} .
                            docker tag devopsmart:${BUILD_NUMBER} ${DOCKERHUB_USERNAME}/devopsmart:${BUILD_NUMBER}
                            docker push ${DOCKERHUB_USERNAME}/devopsmart:${BUILD_NUMBER}
                            docker logout
                        '''
                    }
                }
            }
        }
    }
}
