import re


def dbench_parser(content, outfp):
    score = -1
    if re.search("Throughput", content):
        score = 0
        for config in re.findall("(version.*Running\s+.*?\n)", content,
                re.DOTALL):
            outfp.write(config)

        for summary in re.findall("(Operation\s+Count.*)", content, re.DOTALL):
            outfp.write(summary)
            outfp.write("\n")
        line = content.strip().splitlines()[-1]
        score = line.split()[1]
        return score

if __name__ == "__main__":
    infp = open("1.txt", "r")
    outfp = open("2.txt", "a+")
    content = infp.read()

    score = dbench_parser(content, outfp)

    outfp.close()
    infp.close()
