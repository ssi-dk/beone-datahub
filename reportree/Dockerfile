# syntax=docker/dockerfile:1
# Some later versions of continuumio/miniconda3 cause problems (KeyError('pkgs_dirs'))
FROM continuumio/miniconda3:4.12.0
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install ReporTree
RUN conda install -c etetoolkit -c anaconda -c bioconda python=3.8 biopython=1.77 pandas=1.1.3 numpy=1.19.2 grapetree=2.1 treecluster=1.0.3 ete3 scikit-learn cgmlst-dists git --yes
RUN git clone  --depth 1 --branch v1.1.2 https://github.com/insapathogenomics/ReporTree
RUN chmod 755 ReporTree/reportree.py
WORKDIR /app/ReporTree/scripts/
RUN git clone https://github.com/insapathogenomics/GrapeTree
RUN git clone https://github.com/insapathogenomics/ComparingPartitions
RUN git clone https://github.com/vmixao/vcf2mst.git
WORKDIR /app/ReporTree/
ENV PATH="/app/ReporTree:${PATH}"

# Install FastAPI
RUN conda install -c conda-forge fastapi

# Install Uvicorn
RUN conda install uvicorn

# Install code for REST interface
COPY rest_interface rest_interface/

# Documents which ports are exposed (It is only used for documentation)
EXPOSE 7000

# Start Uvicorn and listen on port
# WORKDIR /app/rest_interface/
# Don't start Uvicorn here but in docker-compose.yml
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]