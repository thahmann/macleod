while read p; do
    echo $p
    python bin/parser.py -f $p --resolve -s http://colore.oor.net/ -b /Users/rpskillet/thesis/colore/ontologies/ --owl > output/$(basename $p .clif)_steps.txt
    cat output/$(basename $p .clif)_steps.txt | sed -n -e '/-- Translation --/,$p' | sed 's/-- Translation --//' | xmllint --format - > output/$(basename $p .clif).owl
    sed -i bkp 's/&lt;=/lt=/g' output/$(basename $p .clif).owl
    sed -i bkp 's/&gt;=/gt=/g' output/$(basename $p .clif).owl
    sed -i bkp 's/&lt;/lt/g' output/$(basename $p .clif).owl
    sed -i bkp 's/&gt;/gt/g' output/$(basename $p .clif).owl
    sed -i bkp 's/#=/#EQUALS/g' output/$(basename $p .clif).owl
done <testing.txt
