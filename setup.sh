# @Author: katie
# @Date:   2018-04-15T14:50:44-05:00
# @Last modified by:   katie
# @Last modified time: 2020-10-24T11:51:45-05:00



# Set up miniconda
# Change directory to the Downloads Folder
cd ~/Downloads
# Download the latest version of Miniconda 3 from the internet
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
# Run the setup script
sh Miniconda3-latest-Linux-x86_64.sh

# Answer yes to all questions

# Create a new miniconda environment that contains the packages that we want
conda create -n logbook python=3.6
conda activate logbook

pip install google-api-python-client
pip install ipykernel

pip install argparse
pip install numpy
pip install httplib2
pip install google_auth_oauthlib
pip install pandas


# Delete the download file
rm Miniconda3-latest-Linux-x86_64.sh

source deactivate logbook
