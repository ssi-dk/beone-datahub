# syntax=docker/dockerfile:1
FROM continuumio/miniconda3:latest
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install ReporTree
RUN conda install -c etetoolkit -c anaconda -c bioconda python=3.8 biopython=1.77 pandas=1.1.3 numpy=1.19.2 grapetree=2.1 treecluster=1.0.3 ete3 scikit-learn cgmlst-dists git --yes
RUN git clone https://github.com/insapathogenomics/ReporTree && chmod 755 ReporTree/reportree.py && cd ReporTree/scripts/ && git clone https://github.com/insapathogenomics/GrapeTree && git clone https://github.com/insapathogenomics/ComparingPartitions && git clone https://github.com/vmixao/vcf2mst.git
ENV PATH="/app/ReporTree:${PATH}"

# Install FastAPI
RUN conda install -c conda-forge fastapi

# Install Uvicorn
RUN conda install uvicorn

# Documents which ports are exposed (It is only used for documentation)
EXPOSE 7000

# Start FastAPI and listen on port