import jp.cafebabe.birthmarks.comparators.Threshold;
import jp.cafebabe.birthmarks.entities.Birthmarks;

def birthmarkList = ["1-gram", "2-gram", "3-gram", "4-gram", "5-gram", "6-gram", "fuc", "uc"] //vom doesnt work 
def comparatorList = ["Cosine", "DiceIndex", "EditDistance", "JaccardIndex", "SimpsonIndex"]
def matcherList = ["Guessed", "RoundRobin", "RoundRobinWithSamePair", "Specified"]

def extract(path, extractor) {
    source = pochi.source(path)
    return extractor.extract(source)
}

def writeToFile(matchResult, filename, directoryName){
    directoryName = "birthmarks/"
    File file = new File(directoryName + filename)

    for (result in matchResult){
        file.append(result)
        file.append("\n")
    }
}

threshold = Threshold.DEFAULT // default threshold (0.75)

header = ["birthmark", "comparator", "matcher", "file1", "file2", "result"]

//update to write all results to a single csv 

for (currentBirthmark in birthmarkList){
    extractor = pochi.extractor(currentBirthmark)
    birthmarks_1 = Arrays.stream(args[0])
        .map(file -> extract(file, extractor))
        .reduce(new Birthmarks(), (b1, b2) -> b1.merge(b2))
    birthmarks_2 = Arrays.stream(args[1])
        .map(file -> extract(file, extractor))
        .reduce(new Birthmarks(), (b1, b2) -> b1.merge(b2))

    for (currentComparator in comparatorList){
        comparator = pochi.comparator(currentComparator)

        for (currentMatcher in matcherList){
            matcher = pochi.matcher(currentMatcher)
            
            matchResult = matcher.match(birthmarks_1, birthmarks_2)
                .map(pair -> comparator.compare(pair))
                .filter(either -> either.isRight())
                .map(either -> either.get())
                .filter(comparison -> comparison.isStolen(threshold))

            filename = args[0].split("/")[-1] + "_" +args[1].split("/")[-1] + ".csv"

            writeToFile(matchResult, filename, "birthmarks/")
        }
    }
}



