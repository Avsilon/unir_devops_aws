/*
 * Jenkinsfile Multibranch - Reto 5
 *
 * Pipeline unificado CI/CD para Jenkins Multibranch Pipeline.
 * - Rama develop: ejecuta flujo CI (Static Test → Deploy staging → Rest Test → Promote)
 * - Rama main:    ejecuta flujo CD (Deploy production → Rest Test solo lectura)
 *
 * Jenkins Multibranch Pipeline clona automáticamente la rama con cambios
 * y expone la variable BRANCH_NAME.
 */
pipeline {
    agent any

    environment {
        GIT_REPO_URL    = 'github.com/Avsilon/unir_devops_aws.git'
        GIT_CREDENTIALS = 'github-token'
        AWS_REGION      = 'us-east-1'
    }

    stages {

        stage('Get Code') {
            steps {
                echo "Rama detectada: ${BRANCH_NAME}"
                echo "Ejecutando pipeline: ${BRANCH_NAME == 'develop' ? 'CI (Staging)' : 'CD (Production)'}"
            }
        }

        // ===============================================================
        //  ETAPAS CI - Solo se ejecutan en la rama develop
        // ===============================================================

        stage('Static Test') {
            when { branch 'develop' }
            steps {
                echo 'Ejecutando análisis estático (Flake8 y Bandit) sobre src/'
                sh '''
                    python3 -m pip install --user flake8 bandit

                    python3 -m flake8 --exit-zero --format=pylint src/ > flake8-report.out
                    python3 -m bandit --exit-zero -r src/ -f html -o bandit-report.html
                '''
            }
            post {
                always {
                    recordIssues tools: [flake8(name: 'Flake8', pattern: 'flake8-report.out')]
                    publishHTML target: [
                        allowMissing:          true,
                        alwaysLinkToLastBuild: true,
                        keepAll:              true,
                        reportDir:            '.',
                        reportFiles:          'bandit-report.html',
                        reportName:           'Bandit Security Report'
                    ]
                }
            }
        }

        stage('Deploy Staging') {
            when { branch 'develop' }
            steps {
                echo 'Construyendo y desplegando en entorno Staging'
                sh '''
                    sam build
                    sam deploy --config-env staging \
                        --no-confirm-changeset \
                        --force-upload \
                        --no-fail-on-empty-changeset \
                        --no-progressbar
                '''
            }
        }

        stage('Rest Test Staging') {
            when { branch 'develop' }
            steps {
                echo 'Ejecutando pruebas de integración contra Staging'
                script {
                    def BASE_URL = sh(
                        script: "aws cloudformation describe-stacks --stack-name todo-list-aws-staging --query 'Stacks[0].Outputs[?OutputKey==`BaseUrlApi`].OutputValue' --region ${AWS_REGION} --output text",
                        returnStdout: true
                    ).trim()
                    echo "BASE_URL: ${BASE_URL}"
                    sh """
                        python3 -m pip install --user pytest requests
                        export BASE_URL=${BASE_URL}
                        python3 -m pytest -s test/integration/todoApiTest.py
                    """
                }
            }
        }

        stage('Promote') {
            when { branch 'develop' }
            steps {
                echo 'Realizando merge de develop a main...'
                withCredentials([string(credentialsId: "${GIT_CREDENTIALS}", variable: 'GITHUB_TOKEN')]) {
                    sh '''
                        git config user.email "ci-jenkins@unir.net"
                        git config user.name "Jenkins CI Pipeline"

                        git fetch origin
                        git checkout -B main origin/main
                        git merge origin/develop --no-edit

                        git remote set-url origin https://${GITHUB_TOKEN}@${GIT_REPO_URL}
                        git push origin main
                    '''
                }
            }
        }

        // ===============================================================
        //  ETAPAS CD - Solo se ejecutan en la rama main
        // ===============================================================

        stage('Deploy Production') {
            when { branch 'main' }
            steps {
                echo 'Construyendo y desplegando en entorno Production'
                sh '''
                    sam build
                    sam deploy --config-env production \
                        --no-confirm-changeset \
                        --force-upload \
                        --no-fail-on-empty-changeset \
                        --no-progressbar
                '''
            }
        }

        stage('Rest Test Production') {
            when { branch 'main' }
            steps {
                echo 'Ejecutando pruebas de integración de solo lectura contra producción'
                script {
                    def BASE_URL = sh(
                        script: "aws cloudformation describe-stacks --stack-name todo-list-aws-production --query 'Stacks[0].Outputs[?OutputKey==`BaseUrlApi`].OutputValue' --region ${AWS_REGION} --output text",
                        returnStdout: true
                    ).trim()
                    echo "BASE_URL: ${BASE_URL}"
                    sh """
                        python3 -m pip install --user pytest requests
                        export BASE_URL=${BASE_URL}
                        python3 -m pytest -s test/integration/todoApiTestReadOnly.py
                    """
                }
            }
        }
    }

    post {
        always {
            echo 'Limpiando workspace'
            cleanWs()
        }
    }
}
