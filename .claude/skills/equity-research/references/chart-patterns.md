# Chart Patterns Reference (LaTeX/TikZ/pgfplots)

## Investment Bank Style Global Settings

```latex
% Add to preamble
\definecolor{IBNavy}{HTML}{003366}
\definecolor{IBGrey}{HTML}{4A5568}
\definecolor{IBLight}{HTML}{F7FAFC}
\definecolor{IBRed}{HTML}{C53030}
\definecolor{IBAmber}{HTML}{D69E2E}
\definecolor{IBGreen}{HTML}{38A169}
\definecolor{IBNVGreen}{HTML}{76B900}
```

## Pattern 1: Radar Chart (6-axis risk profile)

```latex
\usepgfplotslibrary{polar}

\begin{tikzpicture}
\begin{polaraxis}[
    width=9cm, height=9cm,
    xtick={0, 60, 120, 180, 240, 300},
    xticklabels={Dim1, Dim2, Dim3, Dim4, Dim5, Dim6},
    xticklabel style={font=\footnotesize, anchor=center, yshift=6pt},
    ymin=0, ymax=100, ytick={20,40,60,80},
    yticklabel style={font=\tiny, color=IBGrey},
    grid=both, major grid style={thin, IBLight},
    legend style={at={(1.35,1)}, anchor=north west, font=\scriptsize, draw=none},
    axis line style={IBGrey!50},
]
    % Dataset 1 (filled polygon)
    \addplot[IBNavy, thick, fill=IBNavy, fill opacity=0.12, mark=*, mark size=1.5pt]
      coordinates {(0,V1)(60,V2)(120,V3)(180,V4)(240,V5)(300,V6)(360,V1)};
    % Last point must = first to close polygon
    \legend{Portfolio A, Benchmark}
\end{polaraxis}
\end{tikzpicture}
```

## Pattern 2: Swimlane Timeline (catalyst events)

```latex
\begin{tikzpicture}[
    x=2.2cm, % 1 unit = ~1 month
    event/.style={font=\scriptsize, rounded corners=2pt, minimum height=0.55cm,
                  inner sep=3pt, anchor=west},
    track label/.style={font=\scriptsize\bfseries, anchor=east},
]
% Time axis
\draw[IBGrey!60, ->, thick] (-0.3, 0) -- (6.8, 0);
\foreach \x/\m in {0/Mon1, 1/Mon2, 2/Mon3, 3/Mon4, 4/Mon5, 5/Mon6, 6/Mon7} {
    \draw[IBLight] (\x, -0.1) -- (\x, 4.6);
    \node[below, font=\tiny, IBGrey] at (\x, 0) {\m};
}
% Tracks
\node[track label] at (-0.4, 4) {Track 1};
\node[event, fill=IBNavy!15, draw=IBNavy!40] at (0.5, 4) {\tiny Event A};
\node[event, fill=IBNavy!25, draw=IBNavy!60] at (2.5, 4) {\tiny Event B};
% Add more tracks at y=3, 2, 1...
\end{tikzpicture}
```

## Pattern 3: Risk Factor Tree (forest package)

```latex
\usepackage[edges]{forest}

\begin{forest}
    for tree={
        grow'=0, parent anchor=east, child anchor=west,
        edge={IBGrey!60, thick}, l sep=10pt, s sep=2pt,
        font=\scriptsize, minimum height=0.4cm, inner xsep=3pt,
    },
    where level=0{font=\small\bfseries, fill=IBNavy!10, draw=IBNavy!40, rounded corners=2pt}{},
    where level=1{font=\scriptsize\bfseries, fill=IBLight, draw=IBGrey!30, rounded corners=2pt,
                  text width=5.5em, align=center}{},
    where level=2{font=\tiny}{},
    [Root
        [Category A, 4 items
            [A1 Factor name]
            [A2 Factor name]
        ]
        [Category B, 3 items
            [B1 Factor name]
        ]
    ]
\end{forest}
```

## Pattern 4: Scatter/Quadrant Chart (pgfplots)

```latex
\begin{tikzpicture}
\begin{axis}[
    width=14cm, height=10cm,
    xlabel={X Dimension}, ylabel={Y Dimension},
    xmin=0, xmax=1, ymin=0, ymax=1,
    grid=both, grid style={IBLight},
    scatter/classes={
        core={mark=*, draw=IBGreen, fill=IBGreen!60, mark size=4pt},
        wait={mark=*, draw=IBAmber, fill=IBAmber!60, mark size=3.5pt},
        avoid={mark=triangle*, draw=IBRed, fill=IBRed!40, mark size=3pt}
    },
]
    \addplot[scatter, only marks, scatter src=explicit symbolic]
      coordinates {(0.8, 0.9)[core] (0.3, 0.8)[wait] (0.1, 0.2)[avoid]};
    % Labels
    \node[font=\tiny, anchor=south] at (axis cs:0.8,0.9) {Company A};
\end{axis}
\end{tikzpicture}
```

## Pattern 5: Professional Table (booktabs)

```latex
\begin{table}[H]
\centering\scriptsize
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{l c c c X}
\toprule
\textbf{Column A} & \textbf{B} & \textbf{C} & \textbf{D} & \textbf{Notes} \\
\midrule
Row 1 & data & data & \textcolor{IBGreen}{\textbf{+62\%}} & Positive \\
Row 2 & data & data & \textcolor{IBRed}{\textbf{-85\%}} & Negative \\
\bottomrule
\end{tabularx}
\caption{Table title here}
\end{table}
```

## Pattern 6: Key Insight Box (tcolorbox)

```latex
\newtcolorbox{keyinsight}[1][]{
  colback=IBLight, colframe=IBNavy,
  fonttitle=\bfseries, title={#1}, breakable
}

\begin{keyinsight}[One-Line Conclusion]
The actionable takeaway goes here. Be specific: "Buy X below Y, sell above Z."
\end{keyinsight}
```

## Pattern 7: Risk Warning Box

```latex
\newtcolorbox{riskbox}[1][]{
  colback=red!5, colframe=IBRed,
  fonttitle=\bfseries, title={#1}, breakable
}

\begin{riskbox}[Critical Risk Warning]
Compliance-critical information that cannot be abbreviated.
\end{riskbox}
```

## Typography Rules

| Element | Font | Size | Color |
|---------|------|------|-------|
| Chapter title | Bold | \Huge | IBNavy |
| Section title | Bold | \Large | IBNavy |
| Subsection | Bold | \large | IBGrey |
| Body text | Regular | 11pt | Black |
| Table headers | Bold | \scriptsize | Black |
| Chart labels | Sans-serif | \footnotesize | IBGrey |
| Source attribution | Regular | \tiny | grey |
| Risk highlight | Bold | inherit | IBRed/IBAmber/IBGreen |
