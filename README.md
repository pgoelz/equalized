Read me
=======
This repository contains the accompanying code for the paper

> Paul Gölz, Anson Kahng, and Ariel D. Procaccia: Paradoxes in Fair Machine Learning. 2019.

The paper is freely available at <http://paulgoelz.de/papers/equalized.pdf>.

Content
-------
This directory contains four scripts:
- [implementation.py](implementation.py)
  contains an implementation of the geometric algorithm for
  finding optimal equalized-odds allocations subject to a cardinality constraint.
- [fico.ipynb](fico.ipynb)
  is an IPython notebook that allows to replicate our experiments in
  Figure 4. It contains instructions on where to obtain the FICO dataset that we
  used. If you just want to read the code, the easiest way is to use the link above
  to see the preview in your browser, right here on github. If you want to replicate
  our results or do your own experiment in our setting, you need to install the
  dependencies mentioned below. Then, running `jupyter notebook fico.ipynb` opens a
  browser window, in which you can see our simulation results and easily rerun them.
- [resmon.py](resmon.py) implements the recursion step of the algorithm from
  Lemma 5, which allows to find equalized-odds allocation with optimal efficiency,
  while simultaneously satisfying resource monotonicity.
- [resmonplot.py](resmonplot.py) generates visualizations for the algorithm in
  `resmon.py` and was used to construct Figure 3 in the paper. The script is
  supposed to be called from the command line and contains detailed usage
  information when called with `-h`.

Software requirements
---------------------
We used the following software and libraries in the indicated versions. Newer
versions will probably work, but have not been tested.
- Python 3.6.6
- Gurobi 8.0.1 with python bindings
- Matplotlib 2.2.2
- Pandas 0.23.4
- Seaborn 0.9.0
- Jupyter (4.4.0)
For academic use, Gurobi provides free licenses at
<http://www.gurobi.com/academia/for-universities>.

To generate the figures in `resmonplot.py` (and for improved typesetting in the
output of `fico.ipynb`) an up-to-date version of `pdflatex` needs to be installed
and be available from matplotlib and the shell.

Questions
---------
For questions on the code, please contact [Paul Gölz](https://paulgoelz.de).