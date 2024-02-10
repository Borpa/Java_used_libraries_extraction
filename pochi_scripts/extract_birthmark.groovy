import jp.cafebabe.birthmarks.comparators.Threshold;
import jp.cafebabe.birthmarks.entities.Birthmarks;

def extract(path, extractor) {
    source = pochi.source(path)
    return extractor.extract(source)
}

file_output_flag = false

currentBirthmark = args[0]

extractor = pochi.extractor(currentBirthmark)

birthmarks = Arrays.stream(args[1])
    .map(file -> extract(file, extractor))
    .reduce(new Birthmarks(), (b1, b2) -> b1.merge(b2))

birthmarks.forEach(birthmark -> println(birthmark))

if (file_output_flag){
    def data = []
    birthmarks.forEach(birthmark -> data.add(birthmark))

    directoryName = "birthmarks/"
    filename = args[1].split("/")[-1] + args[0] + ".csv"
    def file = new File(directoryName + filename)
    file.text = data
    //file.text = data*.join(",").join(System.lineSeparator())
}