@Library('onfire-shared-library') _

import groovy.json.JsonSlurper

pipeline {
    agent {
        docker {
            label 'DockerAgent'
            image '048549808910.dkr.ecr.us-east-1.amazonaws.com/onfire-ci-image:latest' // Assuming same image as reference
            args '-u root:root -v /var/run/docker.sock:/var/run/docker.sock --privileged'
        }
    }

    parameters {
        string(name: 'BRANCH', defaultValue: 'main', description: 'Repository Branch to build') // Changed default
        booleanParam(name: 'TEST', defaultValue: true, description: 'Run tests') // Default to true
        booleanParam(name: 'DEPLOY', defaultValue: false, description: 'Build and deploy package version to CodeArtifact')
        choice(name: 'ENV', choices: ['development', 'production'], description: 'Select environment context (affects versioning/deletion)')
    }

    environment {
        PROJECT_NAME = 'onfire-blackbird'
        AWS_REGION = "us-east-1"
        AWS_DEFAULT_REGION = "us-east-1"
        CODEARTIFACT_DOMAIN = 'onfire'
        CODEARTIFACT_DOMAIN_OWNER = '048549808910'
        CODEARTIFACT_REPO = 'onfire'
    }

    stages {
        stage('Notify Deployment Start') {
            steps {
                script {
                    echo "Deployment starting for ${env.PROJECT_NAME}..."
                    params.each { k, v ->
                        echo "${k}: ${v}"
                    }
                }
            }
        }

        stage('Install dependencies') {
            steps {
                sh 'apk update && apk add build-base'
                sh 'poetry install --with dev,ai-ner'
            }
        }

        stage('Code Format Check') {
            steps {
                script {
                    sh 'poetry run black --check .'
                    sh 'poetry run isort --check-only .'
                    sh 'poetry run ruff check .'
                }
            }
        }

        stage('Extract Package Info') {
            steps {
                script {
                    def (name, version) = sh(script: "poetry version", returnStdout: true).trim().split(' ', 2)
                    env.PACKAGE_NAME = name.toLowerCase()
                    env.PACKAGE_VERSION = version
                    echo "Package: ${env.PACKAGE_NAME} @ ${env.PACKAGE_VERSION}"
                }
            }
        }

        stage('Set Version for Environment') {
            when {
                expression { params.ENV == 'development' && params.DEPLOY == true }
            }
            steps {
                script {
                    env.PACKAGE_VERSION = onfire.parseVersion(params.BRANCH, params.ENV, env.PACKAGE_VERSION)
                    sh "poetry version ${env.PACKAGE_VERSION}"
                    echo "New Package Version: ${env.PACKAGE_VERSION}"
                }
            }
        }

        stage('Run Tests') {
            when {
                expression { params.TEST == true }
            }
            steps {
                script {
                    sh "poetry run pytest tests/"
                }
            }
        }

        stage('Publish Package to CodeArtifact') {
            when {
                expression { params.DEPLOY == true }
            }
            steps {
                script {
                    echo "Publishing package to CodeArtifact..."
                    sh 'poetry build'
                    def publish_result = onfire.publishToCodeartifact()
                    echo "Publish Result: ${publish_result}"
                }
            }
        }
    }

    post {
        always {
            cleanWs()
             // Revert pyproject.toml if modified by 'poetry version'
            sh 'git checkout -- pyproject.toml || echo "No pyproject.toml changes to revert."'
        }

        success {
            script {
                if (params.DEPLOY) {
                    // Assuming sendSlackNotification is available
                    // sendSlackNotification('success', "Deployment Successful for ${env.PROJECT_NAME} version ${env.PACKAGE_VERSION}", true)
                    echo "Deployment Successful for ${env.PROJECT_NAME} version ${env.PACKAGE_VERSION}"
                }
            }
        }

        failure {
            script {
                 // Assuming sendSlackNotification is available
                 // sendSlackNotification('failure', "Deployment Failed for ${env.PROJECT_NAME}", true)
                 echo "Deployment Failed for ${env.PROJECT_NAME}"
            }
        }
    }
}
