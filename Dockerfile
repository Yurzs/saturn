FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /saturn_socks5_server
WORKDIR /saturn_socks5_server
ADD requirements.txt /saturn_socks5_server/
ADD /saturn /saturn_socks5_server/saturn/
ADD setup.py /saturn_socks5_server/
RUN pip install -r requirements.txt
ENV PYTHONPATH /saturn_socks5_server/
CMD [ "python", "saturn" ]