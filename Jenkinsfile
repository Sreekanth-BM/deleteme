pipeline {
    agent any
    parameters {
        [
            string(name: 'Greeting', defaultValue: 'Hello', description: 'How should I greet the world?'),
            password(name: 'pass', defaultValue: 1234, description: 'Its a password')
        ]
    }    
    stages {
        stage('Echoing') {
            steps {
                sh 'echo "Hello World"'
                echo "${params.Greeting} there"
            }
        }
    }
}
