import jp.cafebabe.birthmarks.comparators.Threshold;
import jp.cafebabe.birthmarks.entities.Birthmarks;

//def birthmarkList = ["1-gram", "2-gram", "3-gram", "4-gram", "5-gram", "6-gram", "fuc", "uc"] //vom doesnt work 
//def comparatorList = ["Cosine", "DiceIndex", "EditDistance", "JaccardIndex", "SimpsonIndex"]
//def matcherList = ["Guessed", "RoundRobin", "RoundRobinWithSamePair", "Specified"]

def comparatorList = ["Cosine", "DiceIndex", "JaccardIndex", "SimpsonIndex"]
def birthmarkList = ["3-gram", "6-gram", "fuc", "uc"]
def matcherList = ["RoundRobinWithSamePair"]

def extract(path, extractor) {
    source = pochi.source(path)
    return extractor.extract(source)
}


//if (args.size() > 2){
//    birthmarkList = [args[2]]
//}

threshold = Threshold.DEFAULT // default threshold (0.75): 0.75 originality, 0.25 similarity
//threshold = new Threshold(0.8)
Random random = new Random()
randomNum = random.nextInt(10 ** 5)
outputFilename = "F:/temp/temp_output_${randomNum}.csv"
File outputFile = new File(outputFilename)
header = "file1,file2,currentBirthmark,currentComparator,currentMatcher,class1,class2,similarity"
outputFile.append(header + "\n")

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
            
            current_settings = args[0] + "," + args[1] + "," + currentBirthmark + "," + currentComparator + "," + currentMatcher + ","

            match_results = matcher.match(birthmarks_1, birthmarks_2)
                .map(pair -> comparator.compare(pair))
                .filter(either -> either.isRight())
                .map(either -> either.get())
                .filter(comparison -> comparison.isStolen(threshold))

            // TODO: randomize name
            match_results.forEach(comparison -> outputFile.append(current_settings + comparison + "\n"))
            //match_results.forEach(comparison -> println(current_settings + comparison))
            // TODO: implement saving results to a temp file
        }
    }
}