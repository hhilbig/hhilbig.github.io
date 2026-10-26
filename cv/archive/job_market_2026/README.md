# Search-specific CVs, 2026 job market (retired)

These wrappers built the CVs submitted to individual searches in fall 2026. On October 26, 2026 the shared source was consolidated to two current CVs: `HHilbig_CV_job_market.tex` (long version for applications) and `HHilbig_CV.tex` (public version on the website). `HHilbig_CV_merit.tex` remains for personnel review.

The wrappers here no longer compile against the current `HHilbig_CV_shared.tex`, because the search-specific switches were removed. To rebuild one exactly, check out commit `a5805a3` and compile the wrapper from `cv/` there.

| Wrapper | Search | What differed from the generic job-market CV |
|---|---|---|
| `CV_UCLA.tex` | UCLA Luskin, Global Public Affairs | Policy reports first, teaching after data, DOIs on datasets |
| `CV_Goldman.tex` | Berkeley Goldman School | Research interests line; admissions paper first among working papers |
| `CV_JHU.tex` | Johns Hopkins School of Government and Policy | UCLA layout plus own research interests and working-paper order; California Policy Lab report first |
| `CV_HKS.tex` | Harvard Kennedy School, Energy and Climate Change | Energy-transition research interests; California Policy Lab report first; tighter item spacing |
| `CV_Chicago.tex` | University of Chicago, climate politics | HKS content with tighter vertical margins (five pages) |
| `CV_UZH.tex` | University of Zurich, politics of inequality | Inequality research interests |
| `Publications_UZH.tex` | University of Zurich | Publication, working-paper, policy and data sections only |

The PDFs actually uploaded are kept in the job-market Dropbox folder under `09_submissions/` (and `01_cv/archive_2026_searches/` for Goldman, whose upload folder holds only the authorization form).
