import argparse
import gzip
import json
import pandas as pd
import plotly.express as px


def drawAccuracies(data, outputFileName):
    accuracies = pd.DataFrame(
        data = [[k, k2, v2[1]/v2[0]] for k, v in data["accuracies"].items() for k2, v2 in v.items()],
        columns = ["Model size", "Text size", "Accuracy"])
    fig1 = px.scatter_3d(
        accuracies,
        x="Model size",
        y="Text size",
        z="Accuracy",
        color="Text size",
        title="Accuracy per model and text size")
    fig1.write_html(outputFileName)


def drawIntervals(data, textName, modelSize, windowSize, threshold, outputFileName):
    intervals = pd.DataFrame(
        data = [[modelName, modelName, interval[0], interval[1], interval[1]-interval[0], sum(bytearray(modelName.encode("utf-8")))]
                for modelName, intervalData in data["intervals"][modelSize][textName]["calculated"][windowSize][threshold].items() for interval in intervalData[0]],
        columns = ["Model", "Group", "Start", "End", "Delta", "Color"])
    intervals = intervals[intervals["Group"].isin(intervals.groupby("Group")["Delta"].sum().nlargest(7).index.tolist())]
    intervals = intervals.append(pd.DataFrame(
        data = [[modelName, "Expected", interval[0], interval[1], interval[1]-interval[0], sum(bytearray(modelName.encode("utf-8")))]
                for modelName, interval in data["intervals"][modelSize][textName]["expected"].items()],
        columns = ["Model", "Group", "Start", "End", "Delta", "Color"]), ignore_index=True)
    fig2 = px.timeline(
        intervals,
        x_start="Start",
        x_end="End",
        y="Group",
        color="Color",
        title=f"{textName}, Model size: {modelSize}, Window size: {windowSize}",
        hover_data=["Model", "Start", "End"],
        color_continuous_scale=[color for _, values in px.colors.qualitative._contents.items() if isinstance(values, list) for color in values])
    fig2.layout.xaxis.type = "linear"
    fig2.data[0].x = intervals.Delta.tolist()
    fig2.write_html(outputFileName)


def main(fileName, accuraciesPrefix, intervalsPrevix, modelSizes, windowSizes, thresholds):
    with gzip.open(fileName, "r") as file:
        data = json.load(file)
        drawAccuracies(data, f"{accuraciesPrefix}.html")
        textName = list(data["intervals"]["1.0"].keys())[3]
        for windowSize in windowSizes:
            for modelSize in modelSizes:
                for threshold in thresholds:
                    drawIntervals(
                        data,
                        textName,
                        str(modelSize),
                        str(windowSize),
                        str(threshold),
                        f"{intervalsPrevix}_{modelSize:.3f}_{windowSize}_{threshold:.3f}.html")
        

if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--data",help="File with the data for the graphs (generated by datagen.py)", required=True)
    parser.add_argument("--accuracies-prefix",help="File prefix to output the accuracies graph", required=True)
    parser.add_argument("--intervals-prefix",help="File prefix to output the intervals graphs", required=True)
    parser.add_argument("--model-sizes",help="List of model sizes to use" , type=float, nargs="+", required=True)
    parser.add_argument("--window-sizes",help="List of window sizes to use" , type=int, nargs="+", required=True)
    parser.add_argument("--thresholds",help="List of window sizes to use" , type=float, nargs="+", required=True)
    args = parser.parse_args()
    main(args.data, args.accuracies_prefix, args.intervals_prefix, args.model_sizes, args.window_sizes, args.thresholds)