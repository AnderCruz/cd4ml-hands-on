pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
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
        pollSCM('* * * * *')
    }

    options {
        timestamps()
    }

    environment {
        MLFLOW_TRACKING_URL = 'http://mlflow:5000'
        MLFLOW_S3_ENDPOINT_URL = 'http://minio:9000'
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
                sh './run_tests.sh'
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

        stage('Production - Register Model and Acceptance Test') {
            when {
                allOf {
                    equals expected: 'default', actual: "${params.ml_pipeline_params_name}"
                    equals expected: 'default', actual: "${params.feature_set_name}"
                    equals expected: 'default', actual: "${params.algorithm_name}"
                    equals expected: 'default', actual: "${params.algorithm_params_name}"
                }
            }

            steps {
                sh 'python3 run_python_script.py acceptance'
            }

            post {
                success {
                    sh "python3 run_python_script.py register_model ${env.MLFLOW_TRACKING_URL} yes"
                }
                failure {
                    sh "python3 run_python_script.py register_model ${env.MLFLOW_TRACKING_URL} no"
                }
            }
        }

        stage('Experiment - Register Model and Acceptance Test') {
            when {
                anyOf {
                    not { equals expected: 'default', actual: "${params.ml_pipeline_params_name}" }
                    not { equals expected: 'default', actual: "${params.feature_set_name}" }
                    not { equals expected: 'default', actual: "${params.algorithm_name}" }
                    not { equals expected: 'default', actual: "${params.algorithm_params_name}" }
                }
            }

            steps {
                sh '''
                    set +e
                    python3 run_python_script.py acceptance
                    set -e
                '''
                sh "python3 run_python_script.py register_model ${env.MLFLOW_TRACKING_URL} no"
            }
        }
    }
}