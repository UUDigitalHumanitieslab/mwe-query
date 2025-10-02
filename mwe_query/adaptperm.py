from sastadev.xlsx import getxlsxdata
import os


def main():
    permpath = './permcomments'
    permfilename = 'mwepermcoments.xlsx'
    permfullname = os.path.join(permpath, permfilename)
    header, data = getxlsxdata(permfullname)


if __name__ == '__main__':
    main()
