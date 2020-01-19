# stop script on error
set -e

# Check to see if root CA file exists, download if not
if [ ! -f ./cert/root-CA.crt ]; then
  printf "\nDownloading AWS IoT Root CA certificate from AWS...\n"
  curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > ./cert/root-CA.crt
fi

# install AWS Device SDK for Python if not already installed
if [ ! -d ./aws-iot-device-sdk-python ]; then
  printf "\nInstalling AWS SDK...\n"
  git clone https://github.com/aws/aws-iot-device-sdk-python.git
  cd aws-iot-device-sdk-python
  python3 setup.py install
  cd ../
fi

# run app using certificates downloaded in package
printf "\nRunning application...\n"
#python3 src/vibration-analyzer.py -e [YOUR-ENDPOINT] -r ./cert/root-CA.crt -c ./cert/[YOUR-DEVICE-NAME].cert.pem -k ./cert/[YOUR-DEVICE-NAME].private.key
python3 src/vibration-analyzer.py -e asq2wj9qjgimw-ats.iot.eu-west-1.amazonaws.com -r ./cert/root-CA.crt -c ./cert/VibrationAnalyzer.cert.pem -k ./cert/VibrationAnalyzer.private.key