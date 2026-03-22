pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '--network jenkins_nw'
        }
    }

    parameters {
        choice(name: 'problem_name', choices: ['houses', 'groceries', 'iris'], description: 'Choose the problem name')
        string(name: 'ml_pipeline_params_name', defaultValue: 'default')
        string(name: 'feature_set_name', defaultValue: 'default')
        string(name: 'algorithm_name', defaultValue: 'default')
        string(name: 'algorithm_params_name', defaultValue: 'default')
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    options {
        timestamps()
    }

    environment {
        MLFLOW_TRACKING_URL = 'http://mlflow:5000'
        MLFLOW_S3_ENDPOINT_URL = 'http://minio:9000'

        // 🔥 ESSENCIAL pro MinIO funcionar
        AWS_ACCESS_KEY_ID = "${ACCESS_KEY}"
        AWS_SECRET_ACCESS_KEY = "${SECRET_KEY}"
    }

    stages {

        stage('Install dependencies') {
            steps {
                sh '''
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run tests') {
            steps {
                sh 'bash run_tests.sh'
            }
        }

        stage('Run ML pipeline') {
            steps {
                sh """
                    python3 run_python_script.py pipeline \
                    ${params.problem_name} \
                    ${params.ml_pipeline_params_name} \
                    ${params.feature_set_name} \
                    ${params.algorithm_name} \
                    ${params.algorithm_params_name}
                """
            }
        }

        stage('Register Model') {
            steps {
                sh 'python3 run_python_script.py acceptance || true'
                sh "python3 run_python_script.py register_model ${env.MLFLOW_TRACKING_URL} no"
            }
        }
    }
}