# syntax=docker/dockerfile:1
FROM continuumio/anaconda3:latest
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /opt/reportree
WORKDIR /opt/reportree
RUN conda create -n reportree -c anaconda -c bioconda -c etetoolkit python=3.6 biopython grapetree=2.1 treecluster=1.0.3 pandas ete3 scikit-learn cgmlst-dists 
RUN git clone https://github.com/insapathogenomics/ReporTree
RUN cd ReporTree/scripts/
RUN git clone https://github.com/insapathogenomics/GrapeTree
RUN git clone https://github.com/insapathogenomics/ComparingPartitions
RUN git clone https://github.com/vmixao/vcf2mst.git