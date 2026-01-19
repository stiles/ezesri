FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.11

# Install Python geo dependencies using pre-built manylinux wheels
# Pin versions that have binary wheels available
RUN pip install --no-cache-dir \
    requests>=2.28.0 \
    numpy==1.26.4 \
    pandas==2.1.4 \
    pyproj==3.6.1 \
    shapely==2.0.4 \
    fiona==1.9.6 \
    geopandas==0.14.4 \
    pyarrow==15.0.2

# Copy function code
COPY handler.py ${LAMBDA_TASK_ROOT}/

# Set the handler
CMD ["handler.lambda_handler"]
