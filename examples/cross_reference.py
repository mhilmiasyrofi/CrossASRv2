import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

import utils

from crossasr import CrossASR


if __name__ == "__main__":
    
    config = utils.readJson("config-trial.json")

    tts = utils.getTTS(config["tts"])
    asrs = utils.getASRS(config["asrs"])
    
    crossasr = CrossASR(tts=tts, asrs=asrs, output_dir=config["output_dir"], recompute=config["recompute"])

    text = "software engineering conference"
    filename = "software_engineering_conference"
    crossasr.processText(text=text, filename=filename)
    crossasr.printResult(text=text, filename=filename)