FROM ubuntu
RUN apt-get -y update; apt-get -y install wget; apt-get -y install python3-pip

RUN wget  http://172.16.240.152/pwh/cpdctl >cpdctl

RUN mv cpdctl.1 cpdctl; chmod +x cpdctl;  mv cpdctl /usr/local/bin/cpdctl; ls -al /usr/local/bin; cpdctl version;

RUN pip3 install ibm_ai_openscale; pip3 install ibm_watson_machine_learning
