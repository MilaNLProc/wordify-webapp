from app import app
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--debug",
    type=bool,
    default=False
)

if __name__ == "__main__":
    args = parser.parse_args()
    app.run(debug=args.debug, host="0.0.0.0")
