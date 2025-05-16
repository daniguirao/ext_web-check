pipeline {
    agent any

    environment {
        TYPE_PROJECT = 'DOCKER_COMPOSE_BUILD'
        PROJECT_NAME = "${env.JOB_NAME}"
        BACKUPDIR = "${env.BACKUPSPACE}/${env.PROJECT_NAME}"
        COMPOSE_FILE = "${env.TARGET_PATH}/docker-compose.yml"
    }
    
    stages {
        stage('🔧 Inicialización de variables') {
            steps {
                script {
                    if (env.TYPE_PROJECT == 'DOCKER_COMPOSE_BUILD') {
                        env.TARGET_PATH = "${env.DOCKERSPATH}/${env.PROJECT_NAME}"
                    } else if (env.TYPE_PROJECT == 'PYTHON_LIB') {
                        env.TARGET_PATH = "${env.PYTHONLIBSPATH}/${env.PROJECT_NAME}"
                    } else {
                        error "Tipo de proyecto desconocido: ${env.TYPE_PROJECT}"
                    }
                    env.COMPOSE_FILE = "${env.TARGET_PATH}/docker-compose.yml"
                    echo "🔧 TARGET_PATH establecido en: ${env.TARGET_PATH}"
                    echo "🔧 COMPOSE_FILE establecido en: ${env.COMPOSE_FILE}"
                }
            }
        }
        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-token',
                    url: 'https://github.com/daniguirao/ext_web-check.git'
            }
        }

        stage('Backup building') {
            steps {
                script {
                    sh "mkdir -p ${env.BACKUPDIR}"
                    sh "rm -rf ${env.BACKUPDIR}/* || true"
                    sh "cp -r ${env.WORKSPACE}/* ${env.BACKUPDIR}/"
                    echo "Backup realizado en: ${env.BACKUPDIR}"
                }
            }
        }

        stage('Crear enlaces simbólicos (solo una vez)') {
            steps {
                script {
                    echo "📁 Generando estructura de enlaces simbólicos..."

                    // Comando bash que crea la estructura y enlaza solo archivos
                    sh """
                        cd ${env.WORKSPACE}

                        find . -type f | while read file; do
                            target_dir="${env.TARGET_PATH}/\$(dirname "\$file")"
                            mkdir -p "\$target_dir"
                            ln -sf "${env.WORKSPACE}/\$file" "\$target_dir/\$(basename "\$file")"
                        done
                    """

                    echo "✅ Enlaces simbólicos creados en ${env.TARGET_PATH}"
                }
            }
        }
        
        stage('STOPPING CURRENT SERVICE') {
            steps {
                script {
                    if (env.TYPE_PROJECT == 'DOCKER_COMPOSE_BUILD') {
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
                    if (env.TYPE_PROJECT == 'PYTHON_LIB') {
                        echo "No se requiere parar el servicio actual en PYTHON_LIB"
                    }
                }
            }
        }

        stage('DEPLOYMENT NEW SERVICE') {
            steps {
                script {
                    if (env.TYPE_PROJECT == 'DOCKER_COMPOSE_BUILD') {
                        try {
                            sh "docker-compose -f ${env.COMPOSE_FILE} up -d --build"
                        } catch (e) {
                            echo "¡Error en el despliegue!"
                            currentBuild.result = 'FAILURE'
                            error("Despliegue fallido, lanzando rollback")
                        }
                    }
                    if (env.TYPE_PROJECT == 'PYTHON_LIB') {
                        echo "No se requiere parar el servicio actual en PYTHON_LIB"
                    }
                }
            }
        }

        stage('CHECKING SERVICE') {
            steps {
                script {
                    if (env.TYPE_PROJECT == 'DOCKER_COMPOSE_BUILD') {
                        def running = sh(script: "docker ps --filter 'name=${env.PROJECT_NAME}' --format '{{.Names}}'", returnStdout: true).trim()
                        if (!running) {
                            error("El servicio ${env.PROJECT_NAME} no está corriendo")
                        }
                    }
                    if (env.TYPE_PROJECT == 'PYTHON_LIB') {
                        echo "No se requiere parar el servicio actual en PYTHON_LIB"
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

                if (fileExists(env.BACKUPDIR) && env.HAD_RUNNING_SERVICE == "true") {
                    echo "✔️ Backup encontrado en ${env.BACKUPDIR}. Restaurando..."

                    // Borra los archivos actuales
                    sh "rm -rf ${env.WORKSPACE}/*"

                    // Restaura desde el backup
                    sh "cp -r ${env.BACKUPDIR}/* ${env.WORKSPACE}/"

                    if (env.TYPE_PROJECT == 'DOCKER_COMPOSE_BUILD') {
                        sh "docker-compose -f ${COMPOSE_FILE} up -d --build || true"
                    }

                    if (env.TYPE_PROJECT == 'PYTHON_LIB') {
                        echo "No se requiere parar el servicio actual en PYTHON_LIB"
                    }
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
