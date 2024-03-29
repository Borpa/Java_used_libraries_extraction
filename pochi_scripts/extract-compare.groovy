import jp.cafebabe.birthmarks.comparators.Threshold;
import jp.cafebabe.birthmarks.entities.Birthmarks;

//def birthmarkList = ["1-gram", "2-gram", "3-gram", "4-gram", "5-gram", "6-gram", "fuc", "uc"] //vom doesnt work 
//def comparatorList = ["Cosine", "DiceIndex", "EditDistance", "JaccardIndex", "SimpsonIndex"]
//def matcherList = ["Guessed", "RoundRobin", "RoundRobinWithSamePair", "Specified"]

//def comparatorList = ["SimpsonIndex"]
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
            
            current_settings = currentBirthmark + "," + currentComparator + "," + currentMatcher + ","

            match_results = matcher.match(birthmarks_1, birthmarks_2)
                .map(pair -> comparator.compare(pair))
                .filter(either -> either.isRight())
                .map(either -> either.get())
                .filter(comparison -> comparison.isStolen(threshold))

            match_results.forEach(comparison -> println(current_settings + comparison))
        }
    }
}