FROM python:3.6-slim-buster

    # get curl
RUN apt update \
    && apt-get install curl -y \
    # get required packaged
    && curl https://raw.githubusercontent.com/UIUC-CS498-Cloud/MP12_PublicFiles/main/requirements.txt --output requirements.txt \
    && yes | pip --no-cache-dir install -r requirements.txt \
    # get python script
    && curl https://raw.githubusercontent.com/UIUC-CS498-Cloud/MP12_PublicFiles/main/classify.py --output classify.py

CMD ["python","-u","classify.py"]