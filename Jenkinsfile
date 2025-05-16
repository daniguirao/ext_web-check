pipeline {
    agent any

    environment {
        COMPOSE_FILE = "docker-compose.yml"
        BACKUP_DIR = ".backup"
        PROJECT_NAME = "ext_web-check"
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
                    def backupDir = "${env.WORKSPACE}/${env.BACKUP_DIR}_${PROJECT_NAME}"
                    def sourceDir = "${env.WORKSPACE}/${PROJECT_NAME}"
                    sh "mkdir -p ${backupDir}"
                    sh "rm -rf ${backupDir}/* || true"
                    sh "cp -r ${sourceDir}/* ${backupDir}/"
                    echo "Backup realizado en: ${backupDir}"
                }
            }
        }

        stage('Parar servicio actual') {
            steps {
                script {
                    def running = sh(
                        script: "docker-compose -f ${env.COMPOSE_FILE} ps -q | grep -q . && echo true || echo false",
                        returnStdout: true
                    ).trim()

                    // Guardamos el estado en una variable de entorno
                    env.HAD_RUNNING_SERVICE = running
                    echo "¿Había servicios corriendo?: ${env.HAD_RUNNING_SERVICE}"

                    // Paramos el servicio si estaba corriendo
                    sh "docker-compose -f ${env.COMPOSE_FILE} down || true"
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

        stage('Ver directorio') {
            steps {
                echo "Ruta del workspace: ${env.WORKSPACE}"
                sh "ls -la ${env.WORKSPACE}"
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
                def backupDir = "${env.WORKSPACE}/${env.BACKUP_DIR}_${PROJECT_NAME}"
                def restoreDir = "${env.WORKSPACE}/${PROJECT_NAME}"

                echo "⚠️ Despliegue fallido. Iniciando rollback..."

                if (fileExists(backupDir) && env.HAD_RUNNING_SERVICE == "true") {
                    echo "✔️ Backup encontrado en ${backupDir}. Restaurando..."

                    // Borra los archivos actuales
                    sh "rm -rf ${restoreDir}/*"

                    // Restaura desde el backup
                    sh "cp -r ${backupDir}/* ${restoreDir}/"

                    // Intenta levantar nuevamente el servicio
                    sh "docker-compose -f ${restoreDir}/docker-compose.yml up -d --build || true"

                    echo "🔁 Rollback completado"
                } else {
                    echo "❌ No se encontró backup para hacer rollback. Estado de la variable HAD_RUNNING_SERVICE: ${env.HAD_RUNNING_SERVICE}"
                }
            }
        }

        success {
            echo "Despliegue realizado correctamente"
        }
    }
}
