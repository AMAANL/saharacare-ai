FROM python:3.10-slim

# Create a non-root user matching Hugging Face's requirements
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy dependency file first to leverage Docker cache
COPY --chown=user requirements.txt requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy all project files
COPY --chown=user . /app

# Expose the internal container port
EXPOSE 7860

# Add the backend directory to the Python path so imports work correctly
ENV PYTHONPATH="/app/backend:${PYTHONPATH}"

# Run the app via gunicorn (production server)
# backend.app points to your app.py in the backend folder
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "backend.app:app"]
