import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    ok = args.url.startswith("rtsp://")
    print("OK" if ok else "INVALID")


if __name__ == "__main__":
    main()
