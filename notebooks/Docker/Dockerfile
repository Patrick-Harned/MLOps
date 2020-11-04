FROM ubuntu

RUN apt-get -y update; apt-get -y install wget; apt-get -y install python3-pip

RUN wget https://github.ibm.com/AILifecycle/cpdctl/releases/download/0.2.33/cpdctl_linux_amd64 >cpdctl

RUN chmod +x cpdctl;  mv cpdctl /usr/local/bin/cpdctl; ls -al /usr/local/bin; cpdctl --version;

RUN pip3 install ibm_ai_openscale; pip3 install ibm_watson_machine_learning
