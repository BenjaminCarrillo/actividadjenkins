pipeline {
    agent any

    // Paso 5: el pipeline revisa GitHub cada ~5 minutos y se ejecuta solo si hay commits nuevos
    triggers {
        pollSCM('H/5 * * * *')
    }

    options {
        timestamps()                                    // hora en cada línea de la consola
        buildDiscarder(logRotator(numToKeepStr: '20'))  // guarda el historial de los últimos 20 builds
    }

    stages {

        stage('Build') {
            steps {
                echo 'Creando entorno virtual e instalando dependencias...'
                sh 'python3 -m venv venv'
                sh 'venv/bin/pip install -r requirements.txt'
                // En Python "compilar" = verificar que el código no tenga errores de sintaxis
                sh 'venv/bin/python -m py_compile app.py'
            }
        }

        stage('Test') {
            steps {
                echo 'Ejecutando pruebas unitarias...'
                sh 'venv/bin/pytest -v --junitxml=test-results.xml'
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Generate Documentation') {
            steps {
                echo 'Generando documentación con Doxygen...'
                sh '''
                    mkdir -p reports
                    doxygen Doxyfile 2> reports/doxygen-warnings.log
                    cat reports/doxygen-warnings.log

                    # Paso 5: informe de actualización y trazabilidad de la documentación
                    {
                        echo "REPORTE DE DOCUMENTACION"
                        echo "========================"
                        echo "Build:   #${BUILD_NUMBER}"
                        echo "Fecha:   $(date '+%Y-%m-%d %H:%M:%S')"
                        echo "Commit:  $(git rev-parse --short HEAD)"
                        echo "Autor:   $(git log -1 --format='%an <%ae>')"
                        echo "Mensaje: $(git log -1 --format='%s')"
                        echo ""
                        echo "Archivos documentados:"
                        ls docs/html | grep '_8py.html' | sed 's/_8py.html/.py/' | sed 's/__/_/g' | sed 's/^/  - /'
                        echo ""
                        echo "Avisos de Doxygen: $(grep -v 'output language' reports/doxygen-warnings.log | grep -c 'warning' || true)"
                    } > reports/reporte-documentacion.txt
                    cat reports/reporte-documentacion.txt
                '''
                archiveArtifacts artifacts: 'docs/html/**, reports/**', fingerprint: true
                publishHTML(target: [
                    reportName  : 'Documentacion Doxygen',
                    reportDir   : 'docs/html',
                    reportFiles : 'index.html, files.html, app_8py.html',
                    reportTitles: 'Inicio, Archivos, app.py',
                    keepAll     : true,
                    alwaysLinkToLastBuild: true
                ])
            }
        }

        stage('Version Control') {
            steps {
                echo 'Subiendo la documentación generada a la rama docs...'
                withCredentials([gitUsernamePassword(credentialsId: 'github-token', gitToolName: 'Default')]) {
                    sh '''
                        COMMIT_CODIGO=$(git rev-parse --short HEAD)
                        git config user.name "Jenkins CI"
                        git config user.email "jenkins@localhost"
                        git checkout -B docs
                        git add -f docs reports
                        git commit -m "Documentacion generada en el build #${BUILD_NUMBER} desde el commit ${COMMIT_CODIGO}" || echo "Sin cambios en la documentacion"
                        git push -f origin docs
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Desplegando la aplicación en el entorno de prueba (puerto 5000)...'
                sh '''
                    if [ -f /var/jenkins_home/app.pid ]; then
                        kill $(cat /var/jenkins_home/app.pid) || true
                    fi
                    JENKINS_NODE_COOKIE=dontKillMe nohup venv/bin/flask --app app run --host 0.0.0.0 --port 5000 > /var/jenkins_home/app.log 2>&1 &
                    echo $! > /var/jenkins_home/app.pid
                    sleep 5
                    curl -f "http://localhost:5000/hello?name=Jenkins"
                '''
            }
        }
    }

    // Paso 5: alertas y notificaciones según el resultado del pipeline
    post {
        success {
            echo "OK: build #${env.BUILD_NUMBER} terminado, documentación actualizada."
        }
        failure {
            script { notificar('FALLIDO', 'Una etapa del pipeline falló. Revisa la consola para corregir el problema.') }
        }
        fixed {
            script { notificar('CORREGIDO', 'El pipeline volvió a funcionar correctamente.') }
        }
    }
}

// Registra la alerta en la consola y en la descripción del build,
// para que se vea directamente en la lista de builds de Jenkins.
def notificar(String estado, String detalle) {
    def alerta = "[Jenkins] ${env.JOB_NAME} #${env.BUILD_NUMBER}: ${estado}"
    echo "ALERTA -> ${alerta}\n${detalle}\nConsola: ${env.BUILD_URL}console"
    currentBuild.description = "${estado}: ${detalle}"
}
