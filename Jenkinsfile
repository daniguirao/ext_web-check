pipeline {
    agent any

    environment {
        CONTAINERS_BASE = "/code/dockers-containers"
        REPO_NAME = "ext_web-check"
        EXTERNAL_PATH = "${CONTAINERS_BASE}/${REPO_NAME}"
        DOCKER_FILE = "${CONTAINERS_BASE}/docker-compose.yml"
    }

    stages {
        stage('Preparar Rutas') {
            steps {
                script {
                    echo "✔ Ruta externa definida: ${EXTERNAL_PATH}"
                    sh """
                        mkdir -p ${EXTERNAL_PATH}
                        chmod 755 ${EXTERNAL_PATH}
                    """
                }
            }
        }

        stage('Crear Enlaces Simbólicos') {
            steps {
                script {
                    def filesToLink = ['app.py', 'Dockerfile', 'requirements.txt']
                    filesToLink.each { file ->
                        sh """
                            ln -sf ${WORKSPACE}/${file} ${EXTERNAL_PATH}/${file}
                            echo "✓ Enlace creado: ${EXTERNAL_PATH}/${file}"
                        """
                    }
                }
            }
        }

        stage('Desplegar Servicio') {
            steps {
                script {
                    sh """
                        docker-compose -f ${DOCKER_FILE} down || true
                        docker-compose -f ${DOCKER_FILE} up -d --build
                    """
                }
            }
        }
    }

    post {
        always {
            echo "✔ Pipeline finalizado | Status: ${currentBuild.result ?: 'SUCCESS'}"
        }
        failure {
            slackSend channel: '#alertas', message: "❌ Fallo en ${REPO_NAME}"
        }
    }
}
