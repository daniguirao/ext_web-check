pipeline {
    agent any

    environment {
        
        CONTAINERS_BASE = "/code/dockers-containers"
		REPO_NAME = "ext_web-check"
        EXTERNAL_PATH = "${CONTAINERS_BASE}/${REPO_NAME}"
		DOCKER_FILE = "${CONTAINERS_BASE}/docker-compose.yml"
    }

    stages {
        // --- Stage 1: Verificar/Crear ruta externa ---
        stage('Preparar Rutas') {
            steps {
                script {
                    echo "✔ Ruta externa definida: ${EXTERNAL_PATH}"

                    // Crear directorio si no existe
                    if (!fileExists(EXTERNAL_PATH)) {
                        sh """
                            mkdir -p ${EXTERNAL_PATH}
                            chmod 755 ${EXTERNAL_PATH}
                        """
                        echo "✓ Directorio creado: ${EXTERNAL_PATH}"
                    } else {
                        echo "✓ El directorio ya existe"
                    }
                }
            }
        }

        // --- Stage 2: Enlazar ficheros locales a ruta externa ---
        stage('Crear Enlaces Simbólicos') {
            steps {
                script {
                    // Lista de ficheros a enlazar (personaliza según tu proyecto)
                    def filesToLink = [
                        'app.py',
                        'Dockerfile',
                        'requirements.txt'
                    ]

                    filesToLink.each { file ->
                        sh """
                            ln -sf ${WORKSPACE}/${file} ${EXTERNAL_PATH}/${file}
                            echo "✓ Enlace creado: ${EXTERNAL_PATH}/${file}"
                        """
                    }
                }
            }
        }

        // --- Stage 3: Desplegar servicio (ejemplo con Docker) ---
        stage('Desplegar Servicio') {
            steps {
                script {
                    dir(EXTERNAL_PATH) {
                        sh """
                            docker-compose -f ${DOCKER_FILE} down
                            docker-compose -f ${DOCKER_FILE} up -d
                        """
                        echo "✓ Servicio desplegado en contenedor Docker"
                    }
                }
            }
        }
    }

    // --- Post-actions para limpieza ---
    post {
        always {
            echo "✔ Pipeline finalizado | Status: ${currentBuild.result ?: 'SUCCESS'}"
        }
        failure {
            slackSend channel: '#alertas', message: "❌ Fallo en ${REPO_NAME}"
        }
    }
}