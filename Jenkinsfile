pipeline {
  // agent any
  agent { docker { image 'python:latest' } }
  parameters {
      string(name: 'Greeting', defaultValue: 'Hello', description: 'How should I greet the world?')
      password(name: 'inflobox_password', defaultValue: 'abcd1234', description: 'Its a password')
  }    
  stages {
      stage('Echoing') {
        steps {
          sh 'echo "Hello World"'
          sh 'echo "${Greeting} there"'
          sh 'echo "${inflobox_password} it is.."'
        }
      }
      stage('Python stuff') {
        steps {
          sh 'python --version'
          sh 'python hello.py'
        }

      }
  }
}
