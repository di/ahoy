DOC = whitepaper
LATEX = pdflatex
BIBTEX = bibtex

.PHONY = all

all : $(DOC).pdf

$(DOC).pdf: $(DOC).tex $(DOC).bib
	$(LATEX) $(DOC)
	$(LATEX) $(DOC)
	$(BIBTEX) $(DOC)
	$(LATEX) $(DOC)
	$(LATEX) $(DOC)

.PHONY : clean

clean:
	rm -rf paper.pdf *.log *.aux *.bbl *.blg *.lof *.lot *.tdo *.toc
