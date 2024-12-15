#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hiregenz_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()



# nvidia-cublas-cu12==12.4.5.8
# nvidia-cuda-cupti-cu12==12.4.127
# nvidia-cuda-nvrtc-cu12==12.4.127
# nvidia-cuda-runtime-cu12==12.4.127
# nvidia-cudnn-cu12==9.1.0.70
# nvidia-cufft-cu12==11.2.1.3
# nvidia-curand-cu12==10.3.5.147
# nvidia-cusolver-cu12==11.6.1.9
# nvidia-cusparse-cu12==12.3.1.170
# nvidia-nccl-cu12==2.21.5
# nvidia-nvjitlink-cu12==12.4.127
# nvidia-nvtx-cu12==12.4.127
# triton==3.1.0