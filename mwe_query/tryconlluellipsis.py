import conllu


def main():
    inputfullname = './conllutest/WR-P-P-H-0000000012.p.1.s.3.conllu'
    # inputfullname = r"D:\Dropbox\various\Resources\nl-parseme-cupt\NL_alpino-ud_1a.connlu"
    with open(inputfullname, 'r', encoding='utf8') as infile:
        data = infile.read()
        sentences = conllu.parse(data)
    for sentence in sentences:
        for token in sentence:
            pass


if __name__ == '__main__':
    main()
