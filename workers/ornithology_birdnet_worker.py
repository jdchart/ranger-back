import birdnet
import sys

def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    model = birdnet.load("acoustic", "2.4", "tf")
    predictions = model.predict(input_path)

    predictions.to_csv(output_path)

if __name__ == "__main__":
    main()