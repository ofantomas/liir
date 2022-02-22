FROM cr.msk.sbercloud.ru/aicloud-jupyter/jupyter-cuda10.1-tf2.3.0-pt1.6.0-gpu

COPY requirements.txt .
COPY install_sc2.sh .

# Install Dependencies
RUN pip install -r requirements.txt
# Install pytorch 0.4.1
RUN pip install torch==0.4.1.post2 -f https://download.pytorch.org/whl/torch_stable.html

# Install StarCraft2 and Maps
RUN bash install_sc2.sh