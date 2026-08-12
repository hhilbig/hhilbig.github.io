.PHONY: all public job-market clean

all: public job-market

public:
	latexmk -pdf -interaction=nonstopmode -halt-on-error HHilbig_CV.tex

job-market:
	latexmk -pdf -interaction=nonstopmode -halt-on-error HHilbig_CV_job_market.tex

clean:
	latexmk -c HHilbig_CV.tex
	latexmk -c HHilbig_CV_job_market.tex
