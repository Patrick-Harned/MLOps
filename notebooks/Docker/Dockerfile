FROM registry.redhat.io/rhel7/rhel
RUN subscription-manager register --username=Patrick.Harned --password=jewelthiefstole12% --auto-attach
RUN yum -y update; yum -y install wget; yum -y install python3-pip

RUN wget https://github.ibm.com/AILifecycle/cpdctl/releases/download/0.2.33/cpdctl_linux_amd64 >cpdctl

RUN chmod +x cpdctl;  mv cpdctl /usr/local/bin/cpdctl; ls -al /usr/local/bin; cpdctl --version;

RUN pip3 install ibm_ai_openscale; pip3 install ibm_watson_machine_learning
