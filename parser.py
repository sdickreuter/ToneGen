import re
import pandas as pd








def parse_file(filepath):
    amps = []
    freqs = []
    phases = []
    # open the file and read through it line by line
    with open(filepath, 'r') as file_object:
        line = file_object.readline()
        while line:
            words = line.split()
            print(words)
            if len(words) == 4:
                if words[0] == "sin":
                    try:
                        amp = float(words[1])
                        freq = complex(words[2])
                        phase = float(words[3])
                    except ValueError as ex:
                        continue
                    amps.append(amp)
                    freqs.append(freq)
                    phases.append(phase)

            line = file_object.readline()

        # create a pandas DataFrame from the list of dicts
        #data = pd.DataFrame([amps,freqs,phases])
        # set the School, Grade, and Student number as the index
        #data.set_index(['School', 'Grade', 'Student number'], inplace=True)
        # consolidate df to remove nans
        #data = data.groupby(level=data.index.names).first()
        # upgrade Score from float to integer
        #data = data.apply(pd.to_numeric, errors='ignore')
    #return data
    return amps, freqs, phases



if __name__ == '__main__':
    filepath = 'tones.txt'
    data = parse_file(filepath)
    print(data)


    # with open('tones.txt') as file:
    #     file_contents = file.read()
    #     print(file_contents)
