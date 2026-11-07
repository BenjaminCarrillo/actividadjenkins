pipeline {
    agent any

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
                sh 'doxygen Doxyfile'
                archiveArtifacts artifacts: 'docs/html/**', fingerprint: true
                publishHTML(target: [
                    reportName : 'Documentacion Doxygen',
                    reportDir  : 'docs/html',
                    reportFiles: 'index.html',
                    keepAll    : true,
                    alwaysLinkToLastBuild: true
                ])
            }
        }

        stage('Version Control') {
            steps {
                echo 'Subiendo la documentación generada a la rama docs...'
                withCredentials([gitUsernamePassword(credentialsId: 'github-token', gitToolName: 'Default')]) {
                    sh '''
                        git config user.name "Jenkins CI"
                        git config user.email "jenkins@localhost"
                        git checkout -B docs
                        git add -f docs
                        git commit -m "Documentacion generada en el build #${BUILD_NUMBER}" || echo "Sin cambios en la documentacion"
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
}