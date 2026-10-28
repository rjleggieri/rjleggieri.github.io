"""Reissue the original NLI report without rerunning or altering its experiments.

All tabulated observations and the embedded figure come from the archived course
PDF. Editorial additions and reference corrections are explicitly identified.
"""
from pathlib import Path
from html import escape
from io import BytesIO
import shutil

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import Font
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle,
    KeepTogether, Preformatted,
)
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / 'docs/archive/Making-DeBERTa-Smarter-original.pdf'
OUTPUT = ROOT / 'output/pdf/Making-DeBERTa-Smarter.pdf'
FIGURE = ROOT / 'paper/figures/original-mnli-data-map.png'

# These values are transcribed, not recomputed estimates.
MNLI_METRICS = [
    ['Evaluation loss', '0.6366', '0.6101'],
    ['Evaluation accuracy', '0.8891', '0.8847'],
    ['Evaluation runtime (s)', '51.546', '48.340'],
    ['Samples per second', '190.412', '203.040'],
    ['Steps per second', '23.804', '25.383'],
]
MNLI_CLASSES = [
    ['Base', 'Contradiction', '0.935', '0.865', '0.899', '3479'],
    ['Base', 'Neutral', '0.821', '0.880', '0.849', '3123'],
    ['Base', 'Entailment', '0.914', '0.925', '0.919', '3213'],
    ['Base', 'Overall', '0.892', '0.889', '0.890', '9815'],
    ['Re-weighted', 'Contradiction', '0.932', '0.862', '0.896', '3479'],
    ['Re-weighted', 'Neutral', '0.818', '0.873', '0.845', '3123'],
    ['Re-weighted', 'Entailment', '0.906', '0.920', '0.913', '3213'],
    ['Re-weighted', 'Overall', '0.887', '0.885', '0.885', '9815'],
]
HANS = [
    ['Constituent','ce_adverb','100.00%','100.00%'],
    ['','ce_after_since_clause','100.00%','100.00%'],
    ['','ce_conjunction','100.00%','100.00%'],
    ['','ce_embedded_under_since','99.60%','99.00%'],
    ['','ce_embedded_under_verb','99.90%','99.90%'],
    ['','cn_adverb','61.90%','63.40%'],
    ['','cn_after_if_clause','0.00%','1.40%'],
    ['','cn_disjunction','0.40%','1.50%'],
    ['','cn_embedded_under_if','68.20%','67.40%'],
    ['','cn_embedded_under_verb','58.60%','68.50%'],
    ['Lexical overlap','le_around_prepositional_phrase','100.00%','99.90%'],
    ['','le_around_relative_clause','99.90%','99.90%'],
    ['','le_conjunction','99.40%','99.30%'],
    ['','le_passive','100.00%','100.00%'],
    ['','le_relative_clause','99.30%','98.80%'],
    ['','ln_conjunction','94.80%','97.70%'],
    ['','ln_passive','98.40%','99.00%'],
    ['','ln_preposition','96.30%','98.50%'],
    ['','ln_relative_clause','94.40%','96.90%'],
    ['','ln_subject/object_swap','99.80%','99.90%'],
    ['Subsequence','se_PP_on_obj','100.00%','100.00%'],
    ['','se_adjective','100.00%','100.00%'],
    ['','se_conjunction','100.00%','99.70%'],
    ['','se_relative_clause_on_obj','100.00%','100.00%'],
    ['','se_understood_object','100.00%','100.00%'],
    ['','sn_NP/S','0.10%','0.00%'],
    ['','sn_NP/Z','3.40%','4.00%'],
    ['','sn_PP_on_subject','66.30%','69.90%'],
    ['','sn_past_participle','2.90%','8.00%'],
    ['','sn_relative_clause_on_subject','81.10%','85.00%'],
    ['Overall accuracy','','77.49%','78.59%'],
]

REFERENCES = [
    ('Clark, K., Luong, M.-T., Le, Q. V., and Manning, C. D. (2020).',
     'ELECTRA: Pre-training Text Encoders as Discriminators Rather Than Generators. ICLR.',
     'https://arxiv.org/abs/2003.10555'),
    ('Devlin, J., Chang, M.-W., Lee, K., and Toutanova, K. (2019).',
     'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. NAACL-HLT, 4171-4186.',
     'https://aclanthology.org/N19-1423/'),
    ('He, P., Liu, X., Gao, J., and Chen, W. (2021).',
     'DeBERTa: Decoding-enhanced BERT with Disentangled Attention. ICLR.',
     'https://arxiv.org/abs/2006.03654'),
    ('He, P., Gao, J., and Chen, W. (2023).',
     'DeBERTaV3: Improving DeBERTa using ELECTRA-Style Pre-Training with Gradient-Disentangled Embedding Sharing. ICLR.',
     'https://arxiv.org/abs/2111.09543'),
    ('Loshchilov, I., and Hutter, F. (2019).',
     'Decoupled Weight Decay Regularization. ICLR.',
     'https://arxiv.org/abs/1711.05101'),
    ('McCoy, R. T., Pavlick, E., and Linzen, T. (2019).',
     'Right for the Wrong Reasons: Diagnosing Syntactic Heuristics in Natural Language Inference. ACL, 3428-3448.',
     'https://aclanthology.org/P19-1334/'),
    ('Poliak, A., Naradowsky, J., Haldar, A., Rudinger, R., and Van Durme, B. (2018).',
     'Hypothesis Only Baselines in Natural Language Inference. *SEM, 180-191.',
     'https://aclanthology.org/S18-2023/'),
    ('Swayamdipta, S., Schwartz, R., Lourie, N., Wang, Y., Hajishirzi, H., Smith, N. A., and Choi, Y. (2020).',
     'Dataset Cartography: Mapping and Diagnosing Datasets with Training Dynamics. EMNLP, 9275-9293.',
     'https://aclanthology.org/2020.emnlp-main.746/'),
    ('Williams, A., Nangia, N., and Bowman, S. R. (2018).',
     'A Broad-Coverage Challenge Corpus for Sentence Understanding through Inference. NAACL-HLT, 1112-1122.',
     'https://aclanthology.org/N18-1101/'),
]

def styles():
    font_dir = Path('C:/Windows/Fonts')
    if (font_dir/'times.ttf').exists():
        for name, file in [('Body','times.ttf'),('BodyBold','timesbd.ttf'),('BodyItalic','timesi.ttf')]:
            pdfmetrics.registerFont(TTFont(name,str(font_dir/file)))
        pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
    else:
        for name, face in [('Body','Times-Roman'),('BodyBold','Times-Bold'),('BodyItalic','Times-Italic')]:
            pdfmetrics.registerFont(Font(name,face,'WinAnsiEncoding'))
        pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
    s=getSampleStyleSheet()
    for key in ['Normal','BodyText']:
        s[key].fontName='Body';s[key].fontSize=10.5;s[key].leading=14.5;s[key].spaceAfter=8
    for key in ['Heading1','Heading2']:
        s[key].fontName='BodyBold';s[key].textColor=colors.HexColor('#17201f')
        s[key].keepWithNext=True
    s['Heading1'].fontSize=15;s['Heading1'].leading=18;s['Heading1'].spaceAfter=12
    s['Heading2'].fontSize=11.5;s['Heading2'].leading=15;s['Heading2'].spaceBefore=12;s['Heading2'].spaceAfter=6
    s.add(ParagraphStyle(name='PaperTitle',fontName='BodyBold',fontSize=23,leading=27,spaceAfter=15))
    s.add(ParagraphStyle(name='Subtitle',fontName='BodyItalic',fontSize=11,leading=15,textColor=colors.HexColor('#52605a'),spaceAfter=12))
    s.add(ParagraphStyle(name='SmallNote',fontName='Body',fontSize=8.5,leading=11.5,spaceAfter=8,textColor=colors.HexColor('#46534d')))
    s.add(ParagraphStyle(name='Ref',fontName='Body',fontSize=9,leading=12,spaceAfter=10,leftIndent=12,firstLineIndent=-12))
    s.add(ParagraphStyle(name='Cell',fontName='Body',fontSize=9,leading=11))
    s.add(ParagraphStyle(name='Equation',fontName='Body',fontSize=10.5,leading=17,leftIndent=20,spaceAfter=5))
    s.add(ParagraphStyle(name='CaptionText',fontName='BodyItalic',fontSize=9,leading=12,spaceAfter=10))
    return s

def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor('#c9cec9'));canvas.line(54,39,558,39)
    canvas.setFont('Body',8);canvas.setFillColor(colors.HexColor('#52605a'))
    canvas.drawString(54,26,'Leggieri | Dataset cartography for NLI | Revised October 28, 2026')
    canvas.drawRightString(558,26,str(doc.page));canvas.restoreState()

def generate():
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    s=styles();story=[]
    def p(text,style='BodyText'):story.append(Paragraph(text,s[style]))
    def h(text):p(text,'Heading2')
    def page(title):
        if story:story.append(PageBreak())
        p(title,'Heading1')
    def table(caption,headers,rows,widths,size=9):
        p(caption,'CaptionText')
        data=[[Paragraph(escape(str(c)),s['Cell']) for c in row] for row in [headers,*rows]]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eee7')),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#52605a')),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#d6dcd5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        story.append(t);story.append(Spacer(1,12))

    p('Dataset Cartography for Robust Natural Language Inference','PaperTitle')
    p('Category-weighted DeBERTa training on MNLI and evaluation on HANS','Subtitle')
    p('Robert Leggieri · The University of Texas at Austin<br/>rjleggieri@utexas.edu')
    p('<b>Revised portfolio edition · October 28, 2026.</b> Originally titled <i>Making DeBERTa Smarter: How Drawing a Map of Data Helped Our Model Stop Making Silly Mistakes</i>. This edition preserves the original reported results and figure, expands the discussion, and corrects verifiable bibliographic and interpretive errors. It is an editorial reissue, not an experimental replication. No models were retrained and no new predictions were generated.','SmallNote')
    h('Abstract')
    p('This course study investigates whether category-weighted training informed by dataset cartography can improve the challenge-set performance of DeBERTa-v3-base. Training dynamics were recorded for 392,702 MNLI examples across five epochs and used to categorize examples as easy to learn, ambiguous, or hard to learn. A custom dataset and Trainer integrated category weights into cross-entropy loss. The selected configuration assigned weights of 0.5, 1.0, and 0.5, respectively, with a variability threshold of 0.2. Reported HANS accuracy increased from 77.49% to 78.59%, while MNLI validation accuracy declined from 88.91% to 88.47%. These observations show a modest, uneven challenge-set improvement accompanied by an in-domain trade-off. They do not establish the causal removal of shortcuts, statistical significance across training runs, or general robustness. The revised discussion examines persistent failures, model-selection uncertainty, competing explanations for hard-example weighting, and the documentation required for a stronger follow-up evaluation.')
    h('1. Introduction')
    p('Natural language inference (NLI) asks whether a hypothesis is entailed by, contradicts, or is neutral with respect to a premise. High benchmark accuracy can coexist with reliance on dataset regularities. Hypothesis-only baselines illustrate one diagnostic route to such artifacts (Poliak et al., 2018), while HANS probes three fallible syntactic heuristics using controlled examples (McCoy et al., 2019).')
    p('Dataset cartography characterizes examples through model-dependent training dynamics (Swayamdipta et al., 2020). This study applies that framework to a re-weighting experiment, retaining the training set while changing the relative contribution of learning regions. The question is whether that intervention changes challenge-set behavior while retaining useful standard validation performance. It is not a test of fairness or general semantic understanding.')

    page('2. Methodology')
    h('2.1 Datasets and evaluation scope')
    p('MNLI provides sentence pairs from multiple genres with entailment, neutral, and contradiction labels (Williams et al., 2018). The original study used 392,702 training examples. Its classification report contains 9,815 evaluated examples: 3,479 contradiction, 3,123 neutral, and 3,213 entailment. The report does not fully document the split identifier or preprocessing that produced these counts. This edition therefore states the evaluated support rather than treating the original general description of approximately 20,000 validation examples as the evaluated sample.')
    p('HANS contains 30,000 examples organized into 30 subcases across lexical overlap, subsequence, and constituent heuristics (McCoy et al., 2019). Each subcase has 1,000 examples and a designated entailment or non-entailment label. This corrects the original description that implied 1,000 examples of each label within every subcase and included negation as a separate HANS heuristic. Table 3 preserves all original subcase results.')
    h('2.2 Model and recorded training settings')
    p('The model was DeBERTa-v3-base. The original DeBERTa architecture uses disentangled attention (He et al., 2021); DeBERTaV3 uses ELECTRA-style replaced-token detection with gradient-disentangled embedding sharing (He et al., 2023; Clark et al., 2020). Encoder pretraining is situated in the broader BERT family (Devlin et al., 2019). The reported configuration has 12 transformer layers, hidden size 768, and 12 attention heads.')
    p('The study reports Hugging Face Transformers and PyTorch, a learning rate of 5 × 10<super>−5</super>, batch size 32, five epochs, and AdamW (Loshchilov and Hutter, 2019). Other Trainer settings were described as defaults. The hardware was an Intel Xeon W-2245 CPU, 32 GB RAM, and an RTX 4080 with 16 GB VRAM. These historical settings are retained, without asserting that unspecified contemporary library defaults reproduce the run.')
    h('2.3 Training dynamics')
    p('A custom <font face="Courier">TrainingDynamicsCallback</font> recorded per-example logits and gold labels at each epoch end in JSON Lines files. For example i, let q(i,e) be the probability assigned to its gold label at epoch e and E = 5. The recorded measures were:')
    for text in [
        'Confidence: μ<sub>i</sub> = (1/E) ∑<super>E</super><sub>e=1</sub> q(i,e)',
        'Variability: σ<sub>i</sub> = √[(1/E) ∑<super>E</super><sub>e=1</sub> (q(i,e) − μ<sub>i</sub>)<super>2</super>]',
        'Correctness: c<sub>i</sub> = (1/E) ∑<super>E</super><sub>e=1</sub> 1[argmax<sub>y</sub> p(y | x<sub>i</sub>,e) = gold<sub>i</sub>]',
    ]:
        p(text,'Equation')
    p('Confidence concerns the gold label, not the most probable label. Variability measures changes across the recorded epochs, and correctness is the fraction of epochs with a correct predicted label. These are properties of a model and training trajectory, rather than intrinsic annotations of difficulty.','SmallNote')

    page('2. Methodology (continued)')
    h('2.4 Data map and learning regions')
    story.append(Image(str(FIGURE),width=504,height=302.4))
    p('Figure 1. MNLI data map generated in this study from DeBERTa-v3-base training dynamics over five epochs. Variability is on the horizontal axis, confidence on the vertical axis, and color denotes correctness.','CaptionText')
    p('Easy examples have high, stable gold-label confidence; hard examples have low, stable confidence; ambiguous examples exhibit greater variability. The original figure describes ambiguous examples as having moderate variability. The operational distinction is relative to the selected threshold, not a universal definition. The report does not provide the full confidence-cutoff rules needed to reconstruct every assignment.')
    h('2.5 Category-weighted loss')
    p('Each example received a weight according to its assigned category. A <font face="Courier">WeightedMNLI_Dataset</font> exposed weights alongside model inputs and labels, and a <font face="Courier">WeightedLossTrainer</font> overrode loss computation. At example level, the reported intervention is:')
    p('L<sub>i</sub> = w<sub>category(i)</sub> · [−∑<super>C</super><sub>c=1</sub> y<sub>i,c</sub> log p<sub>i,c</sub>]','Equation')
    p('The selected weights were easy = 0.5, ambiguous = 1.0, and hard = 0.5, with variability threshold 0.2. The recorded search ranges were easy weights 0.0-0.5, ambiguous weights 1.0-1.2, hard weights 0.0-2.0, and variability thresholds 0.15-0.30. The original report describes categories derived from the baseline run; this is static category weighting, not documented online reassignment.')
    p('Remaining hyperparameters were described as consistent with baseline training. The report does not specify the exact search grid, random seeds, initialization of each candidate, or batch-loss reduction and normalization. Those details should be recovered from implementation records before claiming exact experimental reproducibility.','SmallNote')

    page('3. Reported MNLI results')
    p('Tables 1 and 2 reproduce the original reported values. The baseline model identifier was <font face="Courier">deberta-v3-base_mnli</font>; the selected re-weighted identifier was <font face="Courier">deberta-v3-base_cart_(0.5-1.0-0.5)_mnli</font>.')
    table('Table 1. MNLI evaluation metrics, unchanged.', ['Metric','Base model','Re-weighted model'],MNLI_METRICS,[264,120,120])
    table('Table 2. MNLI classification report, unchanged.', ['Model','Class','Precision','Recall','F1','Support'],MNLI_CLASSES,[83,114,78,70,70,89])
    h('3.1 Accuracy and loss are different observations')
    p('Reported MNLI accuracy changes from 88.91% to 88.47%, a decline of 0.44 percentage points. Evaluation loss decreases from 0.6366 to 0.6101. Lower cross-entropy loss can coexist with lower accuracy because probability assignments and argmax decisions measure different aspects of predictions. The loss values alone do not demonstrate improved calibration; calibration metrics and predictions would be needed.')
    p('The original overall precision, recall, and F1 values are retained without assigning an averaging scheme that was not specified. Small differences between rounded class recalls and aggregate accuracy are compatible with rounding. Evaluation runtime and throughput are historical measurements; this study did not control repeated timing trials and does not establish a speed advantage.')

    page('3. Reported HANS results')
    p('Table 3. Original HANS subcase accuracies, unchanged. Each subcase contains 1,000 examples. Overall values are the original reported aggregate accuracies.','CaptionText')
    data=[['Heuristic','Subcase','Base','Re-weighted'],*HANS]
    cell=ParagraphStyle('HansCell',parent=s['Cell'],fontSize=8,leading=9)
    t=Table([[Paragraph(escape(c),cell) for c in row] for row in data],colWidths=[88,266,70,80],repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eee7')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#52605a')),('LINEBELOW',(0,-1),(-1,-1),.7,colors.HexColor('#52605a')),('TOPPADDING',(0,0),(-1,-1),3.3),('BOTTOMPADDING',(0,0),(-1,-1),3.3),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)]))
    story.append(t)
    p('The observed overall change is +1.10 percentage points. Gains and regressions vary by subcase. The large residual failures in several non-entailment constructions remain important even after the aggregate improvement.','SmallNote')

    page('4. Discussion')
    h('4.1 A modest robustness trade-off')
    p('The clearest result is a shift in performance between evaluation distributions. HANS accuracy improves by 1.10 percentage points while MNLI accuracy declines by 0.44 points. That is a potentially useful trade-off for an application prioritizing the HANS-like constructions, but its value depends on actual error costs and the deployment distribution. The experiment does not identify a universally better model.')
    p('The result is consistent with the possibility that changing the relative influence of learning regions changes what the classifier relies on. It does not isolate that mechanism. Category weighting also changes the effective training objective and gradient contributions; alternative explanations include regularization, altered optimization, and the balance of examples contributing to learning. A uniform-weight control with comparable effective loss scaling, plus controlled ablations, would help distinguish these explanations.')
    h('4.2 Aggregate accuracy hides persistent failures')
    p('Table 3 shows that some subcases are already near ceiling while others remain near zero. For example, <font face="Courier">cn_after_if_clause</font> moves from 0.00% to 1.40%, and <font face="Courier">cn_disjunction</font> from 0.40% to 1.50%. These are improvements in the recorded runs, but they do not solve those constructions. Similarly, <font face="Courier">sn_NP/S</font> changes from 0.10% to 0.00%. A higher overall average should not obscure continued systematic failure.')
    p('The strongest listed constituent gain is <font face="Courier">cn_embedded_under_verb</font>, from 58.60% to 68.50%. Other rows regress, including <font face="Courier">ce_embedded_under_since</font> and <font face="Courier">cn_embedded_under_if</font>. The intervention therefore redistributes errors unevenly. Examining error pairs, confusion patterns, and the linguistic content of improved and degraded examples would provide stronger evidence than the aggregate alone.')
    p('The original discussion inferred a possible weakness from perfect performance on <font face="Courier">le_passive</font>. Perfect accuracy on that subcase is successful classification on those examples; it is not itself evidence that genuine entailments were missed. A claim of heuristic reliance requires contrasts where that heuristic succeeds and fails, and preferably targeted behavioral tests. HANS is useful precisely because its controlled contrasts can expose such differences (McCoy et al., 2019).')
    h('4.3 Difficulty is a model-dependent signal')
    p('The data map is useful as an instrument for inquiry, rather than a final judgment of example quality. Five recorded epochs provide only a short trajectory, and the same example may move between regions under different seeds, checkpoints, learning rates, or architectures. Threshold-based categories discretize continuous signals. A threshold of 0.2 is a selected experimental setting, not a transferable constant established by this study.')

    page('4. Discussion (continued)')
    h('4.4 Hard-example weighting does not diagnose label errors')
    p('The original study reports that increasing hard-example weights worsened both standard and challenge-set performance. Its selected configuration down-weights hard examples as well as easy examples, despite an initial expectation that difficult cases would be informative. This is an important observation, but it does not establish why the hard region was detrimental.')
    p('Swayamdipta et al. (2020) discuss learning regions and data quality, which makes annotation noise a plausible hypothesis. In this experiment, alternatives remain unresolved: ambiguous sentence pairs, rare but correctly labeled constructions, imperfect category rules, limits of the model, and unstable optimization. No human label audit or estimated label-error rate was reported. Down-weighting may suppress valuable rare examples as well as noisy examples.')
    p('A useful follow-up would sample examples from each region for blinded review, separate annotation disagreement from clear errors, and compare region composition across labels and genres. Weighting should then be evaluated against those audits. Low confidence in a gold label is a reason to investigate that example, not permission to treat it as mislabeled.')
    h('4.5 Configuration selection and evaluation independence')
    p('Multiple category weights and variability thresholds were explored before the selected result was reported. The original document does not identify a complete candidate history, an exclusive selection objective, or a challenge set kept untouched until configuration selection finished. Accordingly, HANS should be treated as a reported challenge-set comparison; this edition does not claim an independently held-out estimate of the selected configuration\'s generalization.')
    p('Repeated inspection of a benchmark can make the best observed result optimistic, even when the benchmark is never used for gradient updates. A follow-up should distinguish training data, configuration-selection data, and final evaluation data. It should prerecord which metric determines selection and retain the outcomes of all candidates. If HANS informs design choices, a separate challenge set or a reserved evaluation protocol is needed for a stronger final claim.')
    h('4.6 Uncertainty and paired evidence')
    p('The report contains one baseline-versus-selected-model comparison, without repeated-seed estimates or confidence intervals. The size of the observed gain does not by itself establish that the intervention reliably improves performance across training runs. Item-level paired predictions would permit analysis of changed decisions; repeated training runs would address a different uncertainty, namely sensitivity to stochastic training. Neither source of uncertainty is quantified here.')
    p('HANS examples are generated from structured subcases. Treating all 30,000 observations as independent, identically distributed deployment cases would overstate the breadth of the evidence. Any future interval or significance procedure should state its sampling unit and the relationship between templates, subcases, and the target population. No significance test or interval is retroactively invented for this edition.')

    page('5. Limits, next experiments, and conclusion')
    h('5.1 Reporting and reproducibility limits')
    p('The public report preserves the outcome tables, figure, selected weights, search ranges, and several training settings. It does not provide checkpoints, item predictions, full run logs, exact library versions, tokenization and truncation settings, complete category cutoffs, or all random seeds. It also does not establish whether weighted candidates were initialized from the same pretrained checkpoint or continued from another run. Exact experimental replication requires those records.')
    p('MNLI uses three labels, while HANS distinguishes entailment from non-entailment. A replicable protocol must document how neutral and contradiction outputs are mapped to the HANS decision, including whether non-entailment probabilities are combined or labels are collapsed after prediction. The original report does not resolve that implementation detail. This edition retains its reported HANS scores without reconstructing the missing rule.')
    h('5.2 A focused follow-up design')
    p('<b>First, recover and freeze the protocol.</b> Record dataset versions and split identifiers, preprocessing, category membership, seeds, initialization, optimizer settings, loss normalization, label mapping, and the selection objective. Preserve full candidate results and prediction artifacts.')
    p('<b>Second, test the intervention in parts.</b> Compare unweighted training, easy-only down-weighting, hard-only down-weighting, and the selected combined weighting with matched training settings. Include a control for uniform loss scaling. Repeat the comparison across seeds before treating the selected configuration as reliable.')
    p('<b>Third, investigate the errors.</b> Audit a stratified sample from the learning regions and inspect changed HANS predictions. Evaluate per-subcase behavior and in-domain error costs, rather than optimizing a single aggregate metric alone.')
    p('<b>Fourth, test transfer with independent evidence.</b> Freeze design choices before evaluating a separate challenge distribution or domain dataset. Application-specific relevance, annotation quality, and human review should guide that evaluation. These are proposed experiments, not additional results of the present study.')
    h('5.3 Implications for applied NLP')
    p('The transferable contribution is a workflow: instrument training, inspect example-level behavior, implement a controlled intervention, and compare performance across distributions. Such a workflow can support investigation of a domain-specific text classifier, but MNLI and HANS do not establish utility for vehicle complaints, clinical decisions, or another operational task. Robustness to selected linguistic constructions also does not establish demographic fairness, calibration, or safety.')
    h('5.4 Conclusion')
    p('Category-weighted DeBERTa training produced a reported HANS accuracy increase from 77.49% to 78.59%, alongside a MNLI decline from 88.91% to 88.47%. The preserved subcase results show both improvements and persistent weaknesses. The study supports further investigation of training-data weighting, with stronger selection controls, repeated runs, label audits, and independent evaluation required to establish its mechanism and reliability.')

    page('References')
    p('Verified references used in this revised text. Appendix A records corrections; Appendix B preserves the entire original bibliography, including unresolved entries. Bibliographic verification was performed against publisher or author-hosted primary records on October 28, 2026.','SmallNote')
    for authors,title,url in REFERENCES:
        p(f'{escape(authors)} {escape(title)} <link href="{url}" color="#123f38">{url}</link>','Ref')

    page('Appendix A. Editorial and reference provenance')
    h('A.1 What was preserved')
    p('All values in the original three result tables and the original 1000 × 600 pixel data-map image are preserved. No result was replaced with an inferred correction. Appendix B is an imported facsimile of the original bibliography page. The complete original nine-page report remains available separately as <font face="Courier">Making-DeBERTa-Smarter-original.pdf</font>.')
    h('A.2 Verifiable corrections')
    p('<b>HANS.</b> The original entry attributed a HANS paper to Gardner, Hu, and Baroni (2020). HANS is documented by McCoy, Pavlick, and Linzen (2019), <i>Right for the Wrong Reasons</i>. The revised dataset description and citation use that primary source.')
    p('<b>Dataset cartography.</b> The original title, author list, and arXiv identifier were incorrect. The verified source is Swayamdipta et al. (2020), <i>Dataset Cartography: Mapping and Diagnosing Datasets with Training Dynamics</i>, EMNLP. The original arXiv identifier 2004.04682 resolves to an unrelated mathematics paper.')
    p('<b>Poliak.</b> The original entry combined an incorrect author list with a different title. The revised artifact discussion cites the verified Poliak et al. (2018) <i>Hypothesis Only Baselines in Natural Language Inference</i>. This is a transparent correction to the source supporting that claim, rather than a claim that the original entry was accurate.')
    p('<b>Other retained sources.</b> BERT, DeBERTa, DeBERTaV3, AdamW, ELECTRA, and MNLI have verifiable primary records. Their metadata is normalized in the revised reference list; preprint identifiers are retained where appropriate. DeBERTaV3 is distinguished from the original DeBERTa architecture.')
    h('A.3 Entries retained only in the original bibliography')
    p('<b>Morris, He, and Gao (2020).</b> The original entry titled <i>Debiasing natural language inference models with adversarial training</i> could not be verified as written. Its arXiv identifier 2004.12345 points to an unrelated optimization paper. It is not used as support in the revised text.')
    p('<b>Utama, Santoro, and Wolf (2020).</b> The original entry titled <i>Reducing label noise for visual question answering with auxiliary labeling tasks</i> could not be verified as written. Its arXiv identifier 2003.12345 points to an unrelated graph-theory paper. No intended replacement is guessed.')
    p('<b>Zhou and Bansal (2020).</b> The original title and venue could not be verified as written. A real related paper, <i>Towards Robustifying NLI Models Against Lexical Dataset Biases</i>, by Xiang Zhou and Mohit Bansal, appears at <link href="https://aclanthology.org/2020.acl-main.773/" color="#123f38">ACL 2020, 8759-8771</link>. This is recorded as a related verified work, not silently substituted as proof of the original entry\'s intended identity.')
    h('A.4 Reading Appendix B')
    p('The following page is the original report\'s bibliography, reproduced as a facsimile for provenance. Its original page number and errors are intentionally retained. For sources supporting the revised discussion, use the verified reference list above.')

    # Build cleanly, then append the original reference page without retypesetting it.
    buffer=BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=LETTER,leftMargin=54,rightMargin=54,topMargin=48,bottomMargin=54,
        title='Dataset Cartography for Robust Natural Language Inference',author='Robert Leggieri',
        subject='Revised editorial edition; original experimental observations preserved')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    writer=PdfWriter();writer.append(PdfReader(buffer))
    writer.append(PdfReader(str(ORIGINAL)),pages=(8,9))
    writer.add_metadata({'/Title':'Dataset Cartography for Robust Natural Language Inference','/Author':'Robert Leggieri','/Subject':'Editorial reissue dated October 28, 2026; original results and bibliography preserved'})
    with OUTPUT.open('wb') as f:writer.write(f)
    for dest in [ROOT/'docs/Making-DeBERTa-Smarter.pdf',ROOT/'public/docs/Making-DeBERTa-Smarter.pdf']:
        shutil.copyfile(OUTPUT,dest)
    print(f'Generated {OUTPUT} ({len(PdfReader(str(OUTPUT)).pages)} pages)')

if __name__=='__main__':generate()
