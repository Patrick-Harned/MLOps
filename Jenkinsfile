// Uses Declarative syntax to run commands inside a container.
pipeline {
    agent {
        kubernetes {
            // Rather than inline YAML, in a multibranch Pipeline you could use: yamlFile 'jenkins-pod.yaml'
            // Or, to avoid YAML:
            // containerTemplate {
            //     name 'shell'
            //     image 'ubuntu'
            //     command 'sleep'
            //     args 'infinity'
            // }
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: shell
    image: quay.io/openshift/origin-jenkins-agent-base@sha256:9dc88ba7b0522fb784626af9c545c4d10112f05e125e1c0d98efeb99cf97ecb4
    command:
    - sleep
    args:
    - infinity
'''
            // Can also wrap individual steps:
            // container('shell') {
            //     sh 'hostname'
            // }
            defaultContainer 'shell'
        }
    }
    stages {
        stage('Main') {
            steps {
            	sh 'subscription-manager repos --enable rhel-7-server-optional-rpms --enable rhel-7-server-extras-rpms'
                sh 'pip install --no-cache-dir -r requirements.txt'
                sh 'python ./pipeline/main.py'
            }
        }

    }
}

