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

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t devopsmart:${BUILD_NUMBER} .'
            }
        }
    }
}
