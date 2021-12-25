# TAIPROJECT2G11
File language identifier + file language locator made for a Algorithmic Information Theory project based on Finite-Context Models.

## How to run
The project was implemented in python 3.9, the python3 interpreter is necessary to run code and the pandas and plotly extensions are required for plotting-related code.

The extensions can be installed as follows:
```bash
pip3 install pandas
pip3 install plotly
```
All our other files are detached from these dependencies and can be run without installing them as follows from within the */bin/* folder context.
```bash
python3 lang.py <options>
python3 findlang.py <options>
python3 locatelang.py <options>
python3 locatelanggroups.py <options>
python3 model_compiler.py <options>
```

The options for these scripts are as follows

### lang.py
- --order: sets the order of the model, default is **2**
- --smoothing: sets the model’s smoothing parameter, default is **1**
- --classsource: the name of the file that will be read to generate the model, this value is sensitive to the current folder context
- --input: the name of the file whose cost will be analyzed

### findlang.py
- --classes: folder the class files (models) are stored in, folder context sensitive
- --input: the name of the file whose cost will be analyzed

### locatelang.py
- --classes: folder the class files (models) are stored in, folder context sensitive
- --input: the name of the file whose cost will be analyzed
- --window-size: the size of the window, default is **20**
- --threshold: the maximum average cost of a window to be considered a language, default is **3**

### locatelanggroups.py
- --groups: JSON file containing model groups, folder context sensitive
- --input: the name of the file whose cost will be analyzed
- --window-size: the size of the window, default is **20**
- --threshold: the maximum average cost of a window to be considered a language, default is **3**

The JSON file in the **groups** argument should have the following format:
```json
{
  "group1": ["modelPath1", "modelPath2", "..."],
  "group2": ["..."],
  "..."
}
```

### model_compiler.py
- --order: order of the model, default is **3**
- --smoothing: smoothing parameter of the model, default is **0.1**
- --folder: folder containing the files to be compressed
- --outputprefix: the prefix of the compressed files
- --fraction: the fraction of the file to compress, default is **1**

## Running with options - examples
```bash
python3 lang.py --classsource ../DS/train/aai_PG.latn.Miniafia.bible-train.utf8 --input ../DS/test/aai_PG.latn.Miniafia.bible-test.utf8
python3 model_compiler.py --folder ../DS/train/ --outputprefix models/
python3 findlang.py --classes models/ --input ../DS/test/aai_PG.latn.Miniafia.bible-test.utf8
python3 locatelang.py --classes models/ --input ../DS/test/aai_PG.latn.Miniafia.bible-test.utf8
python3 locatelanggroups.py --groups modelGroups.json --input ../DS/test/aai_PG.latn.Miniafia.bible-test.utf8
```
