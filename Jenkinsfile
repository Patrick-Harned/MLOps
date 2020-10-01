pipeline {
    agent { dockerfile true }
    stages {
        stage('Deploy') {
            steps {
                echo 'Running Container'
	    }
        }
        stage('Testing Deployment') {
            steps {
                # curl command to WML to see if model was deployed successfully
                echo 'Test WML Deployment'
		        sleep 1
            }
        }
        stage('Return results of testing Data') {
            steps {
                # OpenScale
                echo 'OpenScale Evaluation'
		        sleep 1
            }
        }
    }
}
