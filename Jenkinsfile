pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
        DOCKER_IMAGE = "aceest-fitness"
        DOCKER_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out source from GitHub..."
                checkout scm
            }
        }

        stage('Environment Setup') {
            steps {
                echo "Setting up Python virtual environment..."
                sh """
                    python3 -m venv ${VENV_DIR}
                    ${VENV_DIR}/bin/pip install --upgrade pip
                    ${VENV_DIR}/bin/pip install -r requirements.txt
                """
            }
        }

        stage('Lint') {
            steps {
                echo "Running flake8 syntax check..."
                sh "${VENV_DIR}/bin/flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics"
            }
        }

        stage('Unit Tests') {
            steps {
                echo "Running pytest test suite..."
                sh """
                    ${VENV_DIR}/bin/pytest tests/ -v --tb=short \
                        --junitxml=test-results.xml \
                        --cov=app --cov-report=term-missing
                """
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker image: ${DOCKER_IMAGE}:${DOCKER_TAG}..."
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
        }

        stage('Container Smoke Test') {
            steps {
                echo "Running container smoke test..."
                sh """
                    docker run -d --name aceest_smoke_${BUILD_NUMBER} \
                        -p 5001:5000 ${DOCKER_IMAGE}:latest
                    sleep 5
                    curl --fail http://localhost:5001/health
                    docker stop aceest_smoke_${BUILD_NUMBER}
                    docker rm aceest_smoke_${BUILD_NUMBER}
                """
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully. Build #${BUILD_NUMBER} passed all stages."
        }
        failure {
            echo "Pipeline FAILED at build #${BUILD_NUMBER}. Check logs above."
        }
        always {
            echo "Cleaning up workspace..."
            sh "rm -rf ${VENV_DIR} || true"
        }
    }
}
