# CrossASRv2
A Modular Framework Inspired from CrossASR Idea



## Prepare Virtual Environment


### 1. Install the Python development environment on your system

```
sudo apt update
sudo apt install python3-dev python3-pip python3-venv
```

### 2. Create a virtual environment

Create a new virtual environment by choosing a Python interpreter and making a ./env directory to hold it:

```
python3 -m venv --system-site-packages ~/./env
```

Activate the virtual environment using a shell-specific command:

```
source ~/./env/bin/activate  # sh, bash, or zsh
```


## TTSes

### 1. Google

We use [gTTS](https://pypi.org/project/gTTS/) (Google Text-to-Speech), a Python library and CLI tool to interface with Google Translate text-to-speech API. CrossASRv2 use gTTS 2.2.2

```
pip install gTTS
```

#### Trial
```
if [ ! -d "audio/" ]
then 
    mkdir audio
fi

mkdir audio/google/
gtts-cli 'hello world google' --output audio/google/hello.mp3
ffmpeg -i audio/google/hello.mp3  -acodec pcm_s16le -ac 1 -ar 16000 audio/google/hello.wav -y
```

### 2. ResponsiveVoice

We use [rvTTS](https://pypi.org/project/rvtts/), a cli tool for converting text to mp3 files using ResponsiveVoice's API. CrossASRv2 uses rvtts 1.0.1

```
pip install rvtts
```

#### Trial
```
mkdir audio/rv/
rvtts --voice english_us_male --text "hello responsive voice trial" -o audio/rv/hello.mp3
ffmpeg -i audio/rv/hello.mp3  -acodec pcm_s16le -ac 1 -ar 16000 audio/rv/hello.wav -y
```

### 3. Festival

[Festival](http://www.cstr.ed.ac.uk/projects/festival/) is a free TTS written in C++. It is developed by The Centre for Speech Technology Research at the University of Edinburgh. Festival are distributed under an X11-type licence allowing unrestricted commercial and non-commercial use alike. Festival is a command-line program that already installed on Ubuntu 16.04. CrossASRv2 uses Festival 2.5.0

#### Trial
```
sudo apt install festival
mkdir audio/festival/
festival -b "(utt.save.wave (SayText \"hello festival \") \"audio/festival/hello.wav\" 'riff)"
```

### 4. Espeak

[eSpeak](http://espeak.sourceforge.net/) is a compact open source software speech synthesizer for English and other languages. CrossASRv2 uses Espeak 1.48.03

```
sudo apt install espeak

mkdir audio/espeak/
espeak "hello e speak" --stdout > audio/espeak/hello.riff
ffmpeg -i audio/espeak/hello.riff  -acodec pcm_s16le -ac 1 -ar 16000 audio/espeak/hello.wav -y
```


## ASRs

### 1. Deepspeech

[DeepSpeech](https://github.com/mozilla/DeepSpeech) is an open source Speech-To-Text engine, using a model trained by machine learning techniques based on [Baidu's Deep Speech research paper](https://arxiv.org/abs/1412.5567). **CrossASR uses [Deepspeech-0.6.1](https://github.com/mozilla/DeepSpeech/tree/v0.6.1)**

```
pip install deepspeech===0.6.1

if [ ! -d "models/" ]
then 
    mkdir models
fi

cd models
mkdir deepspeech
cd deepspeech 
curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v0.6.1/deepspeech-0.6.1-models.tar.gz
tar xvf deepspeech-0.6.1-models.tar.gz
cd ../../
```

Please follow [this link for more detailed installation](https://github.com/mozilla/DeepSpeech/tree/v0.6.1).

#### Trial
```
deepspeech --model models/deepspeech/deepspeech-0.6.1-models/output_graph.pbmm --lm models/deepspeech/deepspeech-0.6.1-models/lm.binary --trie models/deepspeech/deepspeech-0.6.1-models/trie --audio audio/google/hello.wav
```

### 2. Deepspeech2

[DeepSpeech2](https://github.com/PaddlePaddle/DeepSpeech) is an open-source implementation of end-to-end Automatic Speech Recognition (ASR) engine, based on [Baidu's Deep Speech 2 paper](http://proceedings.mlr.press/v48/amodei16.pdf), with [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) platform.

#### Setup a docker container for Deepspeech2

[Original Source](https://github.com/PaddlePaddle/DeepSpeech#running-in-docker-container)

```
cd models/
git clone https://github.com/PaddlePaddle/DeepSpeech.git
cd DeepSpeech
git checkout tags/v1.1
cp deepspeech2_api.py DeepSpeech/
cd DeepSpeech/models/librispeech/
sh download_model.sh
cd ../../../../
cd models/DeepSpeech/models/lm
sh download_lm_en.sh
cd ../../../../
docker pull paddlepaddle/paddle:1.6.2-gpu-cuda10.0-cudnn7

# please remove --gpus '"device=1"' if you only have one gpu
docker run --name deepspeech2 --rm --gpus '"device=1"' -it -v $(pwd)/models/DeepSpeech:/DeepSpeech -v $(pwd)/europarl/:/DeepSpeech/europarl/  paddlepaddle/paddle:1.6.2-gpu-cuda10.0-cudnn7 /bin/bash

apt-get update
apt-get install git -y
cd DeepSpeech
sh setup.sh
apt-get install libsndfile1-dev -y
``` 

**in case you found error when running the `setup.sh`**

Error solution for `ImportError: No module named swig_decoders`
```
pip install paddlepaddle-gpu==1.6.2.post107
cd DeepSpeech
pip install soundfile
pip install llvmlite===0.31.0
pip install resampy
pip install python_speech_features

wget http://prdownloads.sourceforge.net/swig/swig-3.0.12.tar.gz
tar xvzf swig-3.0.12.tar.gz
cd swig-3.0.12
apt-get install automake -y 
./autogen.sh
./configure
make
make install

cd ../decoders/swig/
sh setup.sh
cd ../../
```

#### Run Deepspeech2 as an API (inside docker container)
```
pip install flask 

CUDA_VISIBLE_DEVICES=0 python deepspeech2-api.py \
    --mean_std_path='models/librispeech/mean_std.npz' \
    --vocab_path='models/librispeech/vocab.txt' \
    --model_path='models/librispeech' \
    --lang_model_path='models/lm/common_crawl_00.prune01111.trie.klm'
```
Then detach from the docker using ctrl+p & ctrl+q after you see `Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)`

#### Run Client from the Terminal (outside docker container)

```
docker exec -it deepspeech2 curl http://localhost:5000/transcribe?fpath=audio/google/hello.wav
```

### 3. Wav2letter++

[wav2letter++](https://github.com/facebookresearch/wav2letter) is a highly efficient end-to-end automatic speech recognition (ASR) toolkit written entirely in C++ by Facebook Research, leveraging ArrayFire and flashlight.

Please find the lastest image of [wav2letter's docker](https://hub.docker.com/r/wav2letter/wav2letter/tags).

```
cd models/
mkdir wav2letter
cd wav2letter

for f in acoustic_model.bin tds_streaming.arch decoder_options.json feature_extractor.bin language_model.bin lexicon.txt tokens.txt ; do wget http://dl.fbaipublicfiles.com/wav2letter/inference/examples/model/${f} ; done

ls -sh
cd ../../
```

#### Run docker inference API
```
docker run --name wav2letter -it --rm -v $(pwd)/europarl/:/root/host/europarl/ -v $(pwd)/models/:/root/host/models/ --ipc=host -a stdin -a stdout -a stderr wav2letter/wav2letter:inference-latest
```
Then detach from the docker using ctrl+p & ctrl+q 

#### Run Client from the Terminal

```
docker exec -it wav2letter sh -c "cat /root/host/audio/google/hello.wav | /root/wav2letter/build/inference/inference/examples/simple_streaming_asr_example --input_files_base_path /root/host/models/wav2letter/"
```

Detail of [wav2letter++ installation](https://github.com/facebookresearch/wav2letter/wiki#Installation) and [wav2letter++ inference](https://github.com/facebookresearch/wav2letter/wiki/Inference-Run-Examples)


### 4. Wit

[Wit](https://wit.ai/) gives an API interface for ASR. We use [pywit](https://github.com/wit-ai/pywit), the Python SDK for Wit. You need to create an WIT account to get access token. CrossASRv2 uses Wit 6.0.0

#### install pywit
```
pip install wit
```

#### Setup Wit access token
```
export WIT_ACCESS_TOKEN=<your Wit access token>
```

#### Check using HTTP API
```
curl -XPOST 'https://api.wit.ai/speech?' \
    -i -L \
    -H "Authorization: Bearer $WIT_ACCESS_TOKEN" \
    -H "Content-Type: audio/wav" \
    --data-binary "@audio/google/hello.wav"
```

**Success Response**
```
HTTP/1.1 100 Continue
Date: Fri, 11 Sep 2020 05:55:51 GMT

HTTP/1.1 200 OK
Content-Type: application/json
Date: Fri, 11 Sep 2020 05:55:52 GMT
Connection: keep-alive
Content-Length: 85

{
  "entities": {},
  "intents": [],
  "text": "hello world google",
  "traits": {}
}
```

#### Trial
```
python models/wit_trial.py
```