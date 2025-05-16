pipeline {
    agent any

    environment {
        COMPOSE_FILE = "docker-compose.yml"
        BACKUP_DIR = ".backup"
        PROJECT_NAME = "miapp"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-token',
                    url: 'https://github.com/daniguirao/ext_web-check.git'
            }
        }

        stage('Backup anterior') {
            steps {
                script {
                    if (fileExists(env.COMPOSE_FILE)) {
                        sh "mkdir -p ${env.BACKUP_DIR}"
                        sh "cp ${env.COMPOSE_FILE} ${env.BACKUP_DIR}/${env.COMPOSE_FILE}.bak"
                    }
                }
            }
        }

        stage('Parar servicio actual') {
            steps {
                script {
                    sh """
                        docker-compose -f ${env.COMPOSE_FILE} down || true
                    """
                }
            }
        }

        stage('Despliegue nuevo') {
            steps {
                script {
                    try {
                        sh "docker-compose -f ${env.COMPOSE_FILE} up -d --build"
                    } catch (e) {
                        echo "¡Error en el despliegue!"
                        currentBuild.result = 'FAILURE'
                        error("Despliegue fallido, lanzando rollback")
                    }
                }
            }
        }

        stage('Verificación del despliegue') {
            steps {
                script {
                    def running = sh(script: "docker ps --filter 'name=${env.PROJECT_NAME}' --format '{{.Names}}'", returnStdout: true).trim()
                    if (!running) {
                        error("El servicio ${env.PROJECT_NAME} no está corriendo")
                    }
                }
            }
        }
    }

    post {
        failure {
            script {
                echo "Rollback en progreso..."
                if (fileExists("${env.BACKUP_DIR}/${env.COMPOSE_FILE}.bak")) {
                    sh """
                        cp ${env.BACKUP_DIR}/${env.COMPOSE_FILE}.bak ${env.COMPOSE_FILE}
                        docker-compose -f ${env.COMPOSE_FILE} up -d --build
                    """
                } else {
                    echo "No se encontró un backup para hacer rollback"
                }
            }
        }

        success {
            echo "Despliegue realizado correctamente"
        }
    }
}
